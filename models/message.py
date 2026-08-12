from models.db import get_db


def add_message(name, email, message):
    """Store a contact form submission."""
    db = get_db()
    db.execute(
        'INSERT INTO messages (name, email, message) VALUES (?, ?, ?)',
        (name, email, message)
    )
    db.commit()


def get_all_messages():
    """Fetch all contact messages, newest first."""
    db = get_db()
    cursor = db.execute(
        'SELECT * FROM messages ORDER BY created_at DESC'
    )
    rows = cursor.fetchall()
    return [dict(row) for row in rows]


def mark_as_read(message_id):
    """Mark a message as read."""
    db = get_db()
    db.execute('UPDATE messages SET is_read = 1 WHERE id = ?', (message_id,))
    db.commit()


def delete_message(message_id):
    """Delete a contact message."""
    db = get_db()
    db.execute('DELETE FROM messages WHERE id = ?', (message_id,))
    db.commit()


def get_unread_count():
    """Return the count of unread messages."""
    db = get_db()
    cursor = db.execute('SELECT COUNT(*) FROM messages WHERE is_read = 0')
    return cursor.fetchone()[0]
