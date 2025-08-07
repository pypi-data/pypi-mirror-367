import pytest
import pytest_asyncio
from datetime import datetime
import os
import tempfile
import yaml
from evolvishub_notification_adapter import Notification, NotificationDB, Config

@pytest_asyncio.fixture
async def temp_config_file():
    """Create a temporary configuration file for testing."""
    config = {
        'database': {
            'path': 'test_notifications.db',
            'directory': './test_data'
        },
        'logging': {
            'enabled': True,
            'level': 'INFO'
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config, f)
        return f.name

@pytest_asyncio.fixture
async def config(temp_config_file):
    """Create a Config instance."""
    return Config(temp_config_file)

@pytest_asyncio.fixture
async def db(config):
    """Create a NotificationDB instance and clean up before each test."""
    async with NotificationDB(config) as db:
        # Clean up database before each test
        async with db._get_connection() as cursor:
            await cursor.execute("DELETE FROM notifications")
            await cursor.execute("DELETE FROM notification_categories")
            await cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('notifications', 'notification_categories')")
        yield db

@pytest.mark.asyncio
async def test_notification_creation():
    """Test creating a notification."""
    notification = Notification("Test message", "info")
    assert notification.message == "Test message"
    assert notification.type == "info"
    assert notification.is_read is False

@pytest.mark.asyncio
async def test_notification_to_dict():
    """Test converting notification to dictionary."""
    notification = Notification("Test message", "info", metadata={"key": "value"})
    data = notification.to_dict()
    assert data["message"] == "Test message"
    assert data["type"] == "info"
    assert data["metadata"] == {"key": "value"}
    assert data["is_read"] is False

@pytest.mark.asyncio
async def test_add_notification(db):
    """Test adding a notification to the database."""
    # Add a notification
    notif_id = await db.add_notification("Test message", "info")
    assert notif_id > 0

@pytest.mark.asyncio
async def test_get_unread_notifications(db):
    """Test getting unread notifications."""
    # Add a notification
    await db.add_notification("Test message", "info")
    
    # Get unread notifications
    unread = await db.get_unread_notifications()
    assert len(unread) == 1
    assert unread[0].message == "Test message"
    assert unread[0].is_read is False

@pytest.mark.asyncio
async def test_mark_as_read(db):
    """Test marking a notification as read."""
    # Add a notification
    notif_id = await db.add_notification("Test message", "info")
    
    # Mark as read
    affected = await db.mark_as_read(notif_id)
    assert affected == 1
    
    # Check if it's marked as read
    unread = await db.get_unread_notifications()
    assert len(unread) == 0 