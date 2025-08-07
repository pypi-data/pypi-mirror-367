import aiosqlite
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import logging
from contextlib import asynccontextmanager
import json
from .notification import Notification
from .category import Category
from .config import Config

class NotificationDB:
    """
    Handles notification CRUD operations in the SQLite database.
    """
    def __init__(self, config: Config):
        """
        Initialize the notification database.
        
        Args:
            config (Config): Configuration object containing database settings.
        """
        self.logger = logging.getLogger('evolvishub_notification_adapter')
        self.db_path = config.get_database_path()
        self.connection = None
        self.cursor = None

    @asynccontextmanager
    async def _get_connection(self):
        """
        Async context manager for database connections.
        Ensures proper connection handling and cleanup.
        """
        try:
            if not self.connection:
                self.connection = await aiosqlite.connect(self.db_path)
                self.connection.row_factory = aiosqlite.Row
            cursor = await self.connection.cursor()
            yield cursor
            await self.connection.commit()
        except Exception as e:
            if self.connection:
                await self.connection.rollback()
            self.logger.error(f"Database operation failed: {e}")
            raise
        finally:
            if cursor:
                await cursor.close()

    async def _ensure_schema(self):
        """Ensure database schema exists."""
        try:
            # Apply initial schema
            with open('evolvishub_notification_adapter/migrations/001_initial_schema.sql', 'r') as f:
                schema = f.read()
                async with self._get_connection() as cursor:
                    await cursor.executescript(schema)
            
            # Apply category schema
            with open('evolvishub_notification_adapter/migrations/002_add_categories.sql', 'r') as f:
                schema = f.read()
                async with self._get_connection() as cursor:
                    await cursor.executescript(schema)
                    
            self.logger.info("Database schema initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize schema: {e}")
            raise

    async def initialize(self):
        """Initialize the database connection and schema."""
        await self._ensure_schema()

    async def add_notification(
        self,
        message: str,
        notif_type: str = "info",
        category_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Add a new notification.
        
        Args:
            message (str): The notification message.
            notif_type (str, optional): Type of notification. Defaults to "info".
            category_id (int, optional): ID of the notification category.
            metadata (dict, optional): Additional metadata for the notification.
            
        Returns:
            int: The inserted notification ID.
        """
        try:
            async with self._get_connection() as cursor:
                sql = """
                INSERT INTO notifications (message, type, category_id, metadata, is_read)
                VALUES (?, ?, ?, ?, 0)
                """
                metadata_json = json.dumps(metadata) if metadata else None
                await cursor.execute(sql, (message, notif_type, category_id, metadata_json))
                notif_id = cursor.lastrowid
                self.logger.info(f"Added notification with ID {notif_id}")
                return notif_id
        except Exception as e:
            self.logger.error(f"Failed to add notification: {e}")
            raise

    async def add_notifications(self, notifications: List[Dict[str, Any]]) -> List[int]:
        """
        Add multiple notifications in bulk.
        
        Args:
            notifications (List[Dict]): List of notification dictionaries.
                Each dict should contain: message, type (optional), category_id (optional), metadata (optional)
                
        Returns:
            List[int]: List of inserted notification IDs.
        """
        try:
            async with self._get_connection() as cursor:
                sql = """
                INSERT INTO notifications (message, type, category_id, metadata, is_read)
                VALUES (?, ?, ?, ?, 0)
                """
                ids = []
                for notif in notifications:
                    metadata_json = json.dumps(notif.get('metadata')) if notif.get('metadata') else None
                    await cursor.execute(sql, (
                        notif['message'],
                        notif.get('type', 'info'),
                        notif.get('category_id'),
                        metadata_json
                    ))
                    ids.append(cursor.lastrowid)
                self.logger.info(f"Added {len(notifications)} notifications with IDs {ids}")
                return ids
        except Exception as e:
            self.logger.error(f"Failed to add notifications in bulk: {e}")
            raise

    async def mark_as_read(self, notif_id: int) -> int:
        """
        Mark a notification as read.
        
        Args:
            notif_id (int): ID of the notification to mark as read.
            
        Returns:
            int: Number of affected rows.
        """
        try:
            async with self._get_connection() as cursor:
                sql = "UPDATE notifications SET is_read = 1 WHERE id = ?"
                await cursor.execute(sql, (notif_id,))
                affected = cursor.rowcount
                self.logger.info(f"Marked notification {notif_id} as read")
                return affected
        except Exception as e:
            self.logger.error(f"Failed to mark notification as read: {e}")
            raise

    async def mark_many_as_read(self, notif_ids: List[int]) -> int:
        """
        Mark multiple notifications as read.
        
        Args:
            notif_ids (List[int]): List of notification IDs to mark as read.
            
        Returns:
            int: Number of affected rows.
        """
        try:
            async with self._get_connection() as cursor:
                placeholders = ','.join('?' * len(notif_ids))
                sql = f"UPDATE notifications SET is_read = 1 WHERE id IN ({placeholders})"
                await cursor.execute(sql, notif_ids)
                affected = cursor.rowcount
                self.logger.info(f"Marked {affected} notifications as read")
                return affected
        except Exception as e:
            self.logger.error(f"Failed to mark notifications as read: {e}")
            raise

    async def get_unread_notifications(self, category_id: Optional[int] = None) -> List[Notification]:
        """
        Get all unread notifications, newest first.
        
        Args:
            category_id (int, optional): Filter by category ID.
            
        Returns:
            List[Notification]: List of unread notifications.
        """
        try:
            async with self._get_connection() as cursor:
                sql = """
                SELECT id, message, type, category_id, metadata, created_at_evie, updated_at_evie, is_read 
                FROM notifications 
                WHERE is_read = 0
                """
                params = []
                if category_id is not None:
                    sql += " AND category_id = ?"
                    params.append(category_id)
                sql += " ORDER BY created_at_evie DESC"
                
                await cursor.execute(sql, params)
                rows = await cursor.fetchall()
                return [Notification(
                    id=row[0],
                    message=row[1],
                    notif_type=row[2],
                    category_id=row[3],
                    metadata=json.loads(row[4]) if row[4] else None,
                    created_at_evie=row[5],
                    updated_at_evie=row[6],
                    is_read=bool(row[7])
                ) for row in rows]
        except Exception as e:
            self.logger.error(f"Failed to get unread notifications: {e}")
            raise

    async def get_all_notifications(
        self,
        category_id: Optional[int] = None,
        notif_type: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Notification]:
        """
        Get all notifications with optional filtering.
        
        Args:
            category_id (int, optional): Filter by category ID.
            notif_type (str, optional): Filter by notification type.
            limit (int, optional): Limit number of results.
            offset (int, optional): Offset for results.
            
        Returns:
            List[Notification]: List of notifications.
        """
        try:
            async with self._get_connection() as cursor:
                sql = """
                SELECT id, message, type, category_id, metadata, created_at_evie, updated_at_evie, is_read 
                FROM notifications 
                WHERE 1=1
                """
                params = []
                
                if category_id is not None:
                    sql += " AND category_id = ?"
                    params.append(category_id)
                    
                if notif_type is not None:
                    sql += " AND type = ?"
                    params.append(notif_type)
                    
                sql += " ORDER BY created_at_evie DESC"
                
                if limit is not None:
                    sql += " LIMIT ?"
                    params.append(limit)
                    
                if offset is not None:
                    sql += " OFFSET ?"
                    params.append(offset)
                
                await cursor.execute(sql, params)
                rows = await cursor.fetchall()
                return [Notification(
                    id=row[0],
                    message=row[1],
                    notif_type=row[2],
                    category_id=row[3],
                    metadata=json.loads(row[4]) if row[4] else None,
                    created_at_evie=row[5],
                    updated_at_evie=row[6],
                    is_read=bool(row[7])
                ) for row in rows]
        except Exception as e:
            self.logger.error(f"Failed to get notifications: {e}")
            raise

    async def get_category(self, category_id: int) -> Optional[Category]:
        """
        Get a category by ID.
        
        Args:
            category_id (int): Category ID.
            
        Returns:
            Optional[Category]: Category object if found, None otherwise.
        """
        try:
            async with self._get_connection() as cursor:
                sql = "SELECT id, name, description, created_at FROM notification_categories WHERE id = ?"
                await cursor.execute(sql, (category_id,))
                row = await cursor.fetchone()
                if row:
                    return Category(
                        id=row[0],
                        name=row[1],
                        description=row[2],
                        created_at=row[3]
                    )
                return None
        except Exception as e:
            self.logger.error(f"Failed to get category: {e}")
            raise

    async def get_categories(self) -> List[Category]:
        """
        Get all notification categories.
        
        Returns:
            List[Category]: List of all categories.
        """
        try:
            async with self._get_connection() as cursor:
                sql = "SELECT id, name, description, created_at_evie FROM notification_categories ORDER BY name"
                await cursor.execute(sql)
                rows = await cursor.fetchall()
                return [Category(
                    id=row[0],
                    name=row[1],
                    description=row[2],
                    created_at=row[3]
                ) for row in rows]
        except Exception as e:
            self.logger.error(f"Failed to get categories: {e}")
            raise

    async def add_category(self, name: str, description: Optional[str] = None) -> int:
        """
        Add a new notification category.
        
        Args:
            name (str): Category name.
            description (str, optional): Category description.
            
        Returns:
            int: The inserted category ID.
        """
        try:
            async with self._get_connection() as cursor:
                sql = "INSERT INTO notification_categories (name, description) VALUES (?, ?)"
                await cursor.execute(sql, (name, description))
                category_id = cursor.lastrowid
                self.logger.info(f"Added category with ID {category_id}")
                return category_id
        except aiosqlite.IntegrityError:
            self.logger.error(f"Category '{name}' already exists")
            raise ValueError(f"Category '{name}' already exists")
        except Exception as e:
            self.logger.error(f"Failed to add category: {e}")
            raise

    async def close(self):
        """Close database connection."""
        if self.connection:
            await self.connection.close()
            self.connection = None
            self.logger.info("Database connection closed")

    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close() 