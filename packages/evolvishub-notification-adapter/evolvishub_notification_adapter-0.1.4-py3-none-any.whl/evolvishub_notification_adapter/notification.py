from typing import Optional, Dict, Any
from datetime import datetime
import logging
import json

class Notification:
    """
    Represents a notification entry.
    """
    VALID_TYPES = {"info", "warning", "error", "success","startup","data_transfer","prediction",
                   "data_processing","system_status","business_operation"}
    MAX_MESSAGE_LENGTH = 1000
    MAX_METADATA_LENGTH = 5000

    def __init__(
        self,
        message: str,
        notif_type: str = "info",
        category_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        created_at_evie: Optional[datetime] = None,
        updated_at_evie: Optional[datetime] = None,
        is_read: bool = False,
        id: Optional[int] = None
    ):
        """
        Initialize a notification.
        
        Args:
            message (str): The notification message.
            notif_type (str, optional): Type of notification. Must be one of: info, warning, error, success. Defaults to "info".
            category_id (int, optional): ID of the notification category.
            metadata (dict, optional): Additional metadata for the notification.
            created_at_evie (datetime, optional): When the notification was created. Defaults to current time.
            updated_at_evie (datetime, optional): When the notification was last updated. Defaults to current time.
            is_read (bool, optional): Whether the notification has been read. Defaults to False.
            id (int, optional): The notification ID. Defaults to None.
            
        Raises:
            ValueError: If notif_type is not valid, message is empty, or metadata is invalid.
        """
        self.logger = logging.getLogger('evolvishub_notification_adapter')
        
        # Validate message
        if not message or not message.strip():
            raise ValueError("Notification message cannot be empty")
        if len(message) > self.MAX_MESSAGE_LENGTH:
            raise ValueError(f"Message length exceeds maximum of {self.MAX_MESSAGE_LENGTH} characters")
            
        # Validate notification type
        if notif_type not in self.VALID_TYPES:
            raise ValueError(f"Invalid notification type. Must be one of: {', '.join(self.VALID_TYPES)}")
            
        # Validate metadata
        if metadata is not None:
            if not isinstance(metadata, dict):
                raise ValueError("Metadata must be a dictionary")
            try:
                metadata_json = json.dumps(metadata)
                if len(metadata_json) > self.MAX_METADATA_LENGTH:
                    raise ValueError(f"Metadata JSON length exceeds maximum of {self.MAX_METADATA_LENGTH} characters")
            except (TypeError, ValueError) as e:
                raise ValueError(f"Invalid metadata: {str(e)}")
            
        self.id = id
        self.message = message.strip()
        self.type = notif_type
        self.category_id = category_id
        self.metadata = metadata or {}
        self.created_at_evie = created_at_evie or datetime.now()
        self.updated_at_evie = updated_at_evie or datetime.now()
        self.is_read = is_read
        
        self.logger.debug(f"Created notification: {self.to_dict()}")

    def to_dict(self) -> dict:
        """
        Convert the notification to a dictionary.
        
        Returns:
            dict: Dictionary representation of the notification.
        """
        return {
            "id": self.id,
            "message": self.message,
            "type": self.type,
            "category_id": self.category_id,
            "metadata": self.metadata,
            "created_at_evie": self.created_at_evie,
            "updated_at_evie": self.updated_at_evie,
            "is_read": self.is_read
        }
        
    def __str__(self) -> str:
        """String representation of the notification."""
        category_str = f" [{self.category_id}]" if self.category_id else ""
        return f"[{self.type.upper()}]{category_str} {self.message} ({'read' if self.is_read else 'unread'})"
        
    def __repr__(self) -> str:
        """Detailed string representation of the notification."""
        return (
            f"Notification(id={self.id}, message='{self.message}', type='{self.type}', "
            f"category_id={self.category_id}, metadata={self.metadata}, "
            f"created_at_evie={self.created_at_evie}, updated_at_evie={self.updated_at_evie}, "
            f"is_read={self.is_read})"
        ) 