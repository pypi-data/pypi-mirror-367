# Evolvishub Notification Adapter

<div align="center">
  <img src="assets/png/eviesales.png" alt="Evolvis AI Logo" width="200"/>
</div>

A flexible notification system adapter for Evolvishub applications. This library provides a simple interface for managing notifications with SQLite backend storage.

## About

This project is part of the [Evolvis AI](https://evolvis.ai) ecosystem, providing intelligent notification management capabilities for Evolvishub applications.

### Author

**Alban Maxhuni, PhD**  
Email: [a.maxhuni@evolvis.ai](mailto:a.maxhuni@evolvis.ai)

## Features

- Async SQLite-based notification storage
- Support for different notification types (info, warning, error, success)
- Category-based notification organization
- Bulk notification operations
- Configurable through YAML or INI files
- Built-in logging system
- Easy to use async API
- Type hints for better IDE support
- Comprehensive test suite with pytest and pytest-asyncio

## Installation

```bash
pip install evolvishub-notification-adapter
```

## Quick Start

```python
import asyncio
from evolvishub_notification_adapter import Notification, NotificationDB, Config, Category

async def main():
    # Initialize with your application's configuration file
    config = Config("/path/to/your/config.yaml")  # or .ini file
    
    # Use async context manager for proper resource management
    async with NotificationDB(config) as db:
        # Add a simple notification
        notification_id = await db.add_notification("Hello, World!", "info")

        # Add a notification with category and metadata
        category_id = await db.add_category("updates", "System updates")
        notification_id = await db.add_notification(
            "New version available",
            "info",
            category_id=category_id,
            metadata={"version": "1.2.0", "changes": ["Bug fixes", "New features"]}
        )

        # Get unread notifications
        unread = await db.get_unread_notifications()
        for notif in unread:
            print(f"Unread: {notif.message}")

        # Mark notifications as read
        await db.mark_as_read(notification_id)  # Single notification
        await db.mark_many_as_read([1, 2, 3])  # Multiple notifications

        # Get all notifications with filters
        all_notifs = await db.get_all_notifications(
            category_id=category_id,
            notif_type="info",
            limit=10,
            offset=0
        )

# Run the async main function
asyncio.run(main())
```

## Advanced Usage

### Working with Categories

```python
async def manage_categories():
    async with NotificationDB(config) as db:
        # Add a new category
        category_id = await db.add_category("alerts", "Important system alerts")

        # Get all categories
        categories = await db.get_categories()
        for category in categories:
            print(f"Category: {category.name} - {category.description}")

        # Get notifications by category
        category_notifs = await db.get_all_notifications(category_id=category_id)

# Run the async function
asyncio.run(manage_categories())
```

### Bulk Operations

```python
async def bulk_operations():
    async with NotificationDB(config) as db:
        # Add multiple notifications at once
        notifications = [
            {
                "message": "System update available",
                "type": "info",
                "category_id": category_id,
                "metadata": {"version": "1.2.0"}
            },
            {
                "message": "Disk space low",
                "type": "warning",
                "category_id": category_id,
                "metadata": {"space_left": "500MB"}
            }
        ]
        notif_ids = await db.add_notifications(notifications)

        # Mark multiple notifications as read
        await db.mark_many_as_read(notif_ids)

# Run the async function
asyncio.run(bulk_operations())
```

### Working with Metadata

```python
async def metadata_example():
    async with NotificationDB(config) as db:
        # Add notification with metadata
        notification_id = await db.add_notification(
            "User action required",
            "warning",
            metadata={
                "user_id": 123,
                "action": "verify_email",
                "expires_at": "2024-03-20T00:00:00Z"
            }
        )

        # Get notification and access metadata
        notifications = await db.get_all_notifications()
        notification = notifications[0]
        user_id = notification.metadata.get("user_id")

# Run the async function
asyncio.run(metadata_example())
```

## Configuration

The library requires a configuration file to be provided by your application. You can use either YAML or INI format.

### YAML Configuration Example

Create a `config.yaml` file in your application:

```yaml
database:
  path: notifications.db
  directory: ./data

logging:
  enabled: true
  level: INFO
```

### INI Configuration Example

Create a `config.ini` file in your application:

```ini
[database]
path = notifications.db
directory = ./data

[logging]
enabled = true
level = INFO
```

### Configuration Options

- `database.path`: Name of the SQLite database file
- `database.directory`: Directory where the database file will be stored
- `logging.enabled`: Enable/disable logging
- `logging.level`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

## Testing

The library includes a comprehensive test suite using pytest and pytest-asyncio. The tests cover:

- Basic notification operations (create, read, update)
- Category management
- Bulk operations
- Error handling
- Database state management
- Async context manager functionality

To run the tests:

```bash
# Install test dependencies
pip install -e ".[test]"

# Run all tests
pytest

# Run tests with coverage
pytest --cov=evolvishub_notification_adapter

# Run specific test file
pytest tests/test_notification.py

# Run tests with verbose output
pytest -v
```

## Requirements

- Python 3.7 or higher
- aiosqlite 0.19.0 or higher
- PyYAML 6.0.1 or higher
- pytest 7.0.0 or higher (for testing)
- pytest-asyncio 0.21.0 or higher (for testing)

## Development

To set up the development environment:

```bash
# Clone the repository
git clone https://github.com/yourusername/evolvishub-notification-adapter.git
cd evolvishub-notification-adapter

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
flake8
black .
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and ensure they pass
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.