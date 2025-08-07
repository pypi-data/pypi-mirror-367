from typing import Optional
from datetime import datetime
import logging

class Category:
    """
    Represents a notification category.
    """
    def __init__(self, name: str, description: Optional[str] = None, id: Optional[int] = None, created_at: Optional[datetime] = None):
        """
        Initialize a notification category.
        
        Args:
            name (str): Category name (must be unique).
            description (str, optional): Category description.
            id (int, optional): Category ID.
            created_at (datetime, optional): When the category was created.
            
        Raises:
            ValueError: If name is empty or invalid.
        """
        self.logger = logging.getLogger('evolvishub_notification_adapter')
        
        if not name or not name.strip():
            raise ValueError("Category name cannot be empty")
            
        if not name.isalnum() and not all(c.isalnum() or c == '_' for c in name):
            raise ValueError("Category name can only contain alphanumeric characters and underscores")
            
        self.id = id
        self.name = name.strip().lower()
        self.description = description
        self.created_at = created_at or datetime.now()
        
        self.logger.debug(f"Created category: {self.to_dict()}")
        
    def to_dict(self) -> dict:
        """
        Convert the category to a dictionary.
        
        Returns:
            dict: Dictionary representation of the category.
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at
        }
        
    def __str__(self) -> str:
        """String representation of the category."""
        return f"{self.name} ({self.description or 'No description'})"
        
    def __repr__(self) -> str:
        """Detailed string representation of the category."""
        return f"Category(id={self.id}, name='{self.name}', description='{self.description}', created_at={self.created_at})" 