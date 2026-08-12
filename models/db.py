import sqlite3
import datetime
from flask import g, current_app

# Register custom timestamp converters to prevent Python 3.12+ sqlite3 deprecation warnings
sqlite3.register_converter("timestamp", lambda v: datetime.datetime.fromisoformat(v.decode()))
sqlite3.register_converter("TIMESTAMP", lambda v: datetime.datetime.fromisoformat(v.decode()))


def get_db():
    """Get the database connection for the current application context."""
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE_PATH'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
        # Enable foreign keys
        g.db.execute('PRAGMA foreign_keys = ON')
    return g.db


def close_db(e=None):
    """Close the database connection at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db(app):
    """Initialize the database schema."""
    with app.app_context():
        db = get_db()
        with open(app.config['SCHEMA_PATH'], 'r') as f:
            db.executescript(f.read())
        db.commit()
