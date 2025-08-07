import pytest
import os
import asyncio
from evolvishub_notification_adapter.notification_db import NotificationDB
from evolvishub_notification_adapter.notification import Notification

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def db():
    """Create a test database instance."""
    # Use an in-memory database for testing
    db = NotificationDB(":memory:")
    await db.initialize()
    
    # Add test categories
    async with db:
        await db.add_category("Test Category 1")
        await db.add_category("Test Category 2")
    
    yield db
    
    # Cleanup
    await db.close()

@pytest.fixture(scope="function")
async def sample_notification():
    """Create a sample notification for testing."""
    return Notification(
        message="Test notification",
        notif_type="test",
        category_id=1,
        metadata={"key": "value"}
    )

@pytest.fixture(scope="function")
async def populated_db(db, sample_notification):
    """Create a database with some test data."""
    async with db:
        # Add some notifications
        await db.add_notification(sample_notification)
        await db.add_notification(Notification(
            message="Another test notification",
            notif_type="alert",
            category_id=2
        ))
        
        # Mark one as read
        notifications = await db.get_all_notifications()
        await db.mark_as_read(notifications[0].id)
    
    return db 