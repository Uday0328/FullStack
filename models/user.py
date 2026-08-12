from werkzeug.security import generate_password_hash, check_password_hash
from models.db import get_db


def get_user_by_username(username):
    """Fetch a user by username."""
    db = get_db()
    cursor = db.execute(
        'SELECT * FROM users WHERE username = ?', (username,)
    )
    row = cursor.fetchone()
    return dict(row) if row else None


def create_user(username, password):
    """Create a new admin user with a hashed password."""
    db = get_db()
    password_hash = generate_password_hash(password)
    db.execute(
        'INSERT INTO users (username, password_hash) VALUES (?, ?)',
        (username, password_hash)
    )
    db.commit()


def verify_password(username, password):
    """Verify a username/password combination. Returns True if valid."""
    user = get_user_by_username(username)
    if not user:
        return False
    return check_password_hash(user['password_hash'], password)


def user_exists(username):
    """Check if a user already exists."""
    return get_user_by_username(username) is not None
