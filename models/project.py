# pyrefly: ignore [missing-import]
from models.db import get_db


def get_all_projects():
    """Fetch all projects ordered by featured first, then by date."""
    db = get_db()
    cursor = db.execute(
        'SELECT * FROM projects ORDER BY is_featured DESC, id DESC'
    )
    rows = cursor.fetchall()
    return [dict(row) for row in rows]


def get_featured_projects():
    """Fetch only featured projects."""
    db = get_db()
    cursor = db.execute(
        'SELECT * FROM projects WHERE is_featured = 1 ORDER BY id DESC'
    )
    rows = cursor.fetchall()
    return [dict(row) for row in rows]


def get_project_by_id(project_id):
    """Fetch a single project by ID."""
    db = get_db()
    cursor = db.execute(
        'SELECT * FROM projects WHERE id = ?', (project_id,)
    )
    row = cursor.fetchone()
    return dict(row) if row else None


def add_project(title, description, technologies, date, github_url='', demo_url='', is_featured=0, status='Completed'):
    """Insert a new project into the database."""
    db = get_db()
    db.execute(
        '''INSERT INTO projects (title, description, technologies, date, github_url, demo_url, is_featured, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        (title, description, technologies, date, github_url, demo_url, int(is_featured), status)
    )
    db.commit()


def delete_project(project_id):
    """Delete a project by ID."""
    db = get_db()
    db.execute('DELETE FROM projects WHERE id = ?', (project_id,))
    db.commit()


def toggle_featured(project_id):
    """Toggle the featured status of a project."""
    db = get_db()
    db.execute(
        'UPDATE projects SET is_featured = CASE WHEN is_featured = 1 THEN 0 ELSE 1 END WHERE id = ?',
        (project_id,)
    )
    db.commit()


def update_project(project_id, title, description, technologies, date, github_url='', demo_url='', is_featured=0, status='Completed'):
    """Update an existing project in the database."""
    db = get_db()
    db.execute(
        '''UPDATE projects
           SET title = ?, description = ?, technologies = ?, date = ?,
               github_url = ?, demo_url = ?, is_featured = ?, status = ?
           WHERE id = ?''',
        (title, description, technologies, date, github_url, demo_url, int(is_featured), status, project_id)
    )
    db.commit()

