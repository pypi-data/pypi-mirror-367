-- Drop existing tables and triggers if they exist
DROP TABLE IF EXISTS notifications;
DROP TRIGGER IF EXISTS update_notifications_updated_at_evie;

-- Create notifications table
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message TEXT NOT NULL,
    type TEXT NOT NULL DEFAULT 'info',
    category_id INTEGER,
    metadata TEXT,
    created_at_evie TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at_evie TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN NOT NULL DEFAULT 0
);

-- Create indexes after table creation
CREATE INDEX idx_notifications_created_at_evie ON notifications(created_at_evie);
CREATE INDEX idx_notifications_updated_at_evie ON notifications(updated_at_evie);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);

-- Create trigger after table creation
CREATE TRIGGER update_notifications_updated_at_evie
AFTER UPDATE ON notifications
BEGIN
    UPDATE notifications SET updated_at_evie = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END; 