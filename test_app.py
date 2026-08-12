"""
Automated Unit and Integration Test Suite for Portfolio Application.
Uses Flask's test_client to test all public and admin endpoints.
"""
import os
import unittest
import tempfile
from app import create_app
from models.db import init_db
from models.project import add_project, get_all_projects, get_project_by_id
from models.user import create_user


class PortfolioAppTestCase(unittest.TestCase):

    def setUp(self):
        """Set up test environment with a temporary SQLite database."""
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        
        # Configure app for testing
        self.app = create_app('testing')
        self.app.config['DATABASE_PATH'] = self.db_path
        
        self.client = self.app.test_client()

        with self.app.app_context():
            init_db(self.app)
            create_user('admin', 'Admin@2026')
            add_project(
                title='Test Project Alpha',
                description='Alpha test project description.',
                technologies='Python, Flask',
                date='May 2026',
                github_url='https://github.com/test/alpha',
                demo_url='https://demo.com/alpha',
                is_featured=1,
                status='Completed'
            )

    def tearDown(self):
        """Clean up temporary files."""
        os.close(self.db_fd)
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    # ── Public Routes ──────────────────────────────────────────────────────────

    def test_index_page(self):
        """Test home page loads successfully."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Uday', response.data)

    def test_projects_api(self):
        """Test projects JSON API endpoint."""
        response = self.client.get('/api/projects')
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data['count'], 1)
        self.assertEqual(json_data['projects'][0]['title'], 'Test Project Alpha')

    def test_contact_api_success(self):
        """Test contact form API submission with valid data."""
        payload = {
            'name': 'Test User',
            'email': 'user@example.com',
            'message': 'Hello from automated unit test!'
        }
        response = self.client.post('/api/contact', json=payload)
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertTrue(json_data['success'])

    def test_contact_api_invalid(self):
        """Test contact form API with missing fields."""
        payload = {'name': '', 'email': 'bademail', 'message': ''}
        response = self.client.post('/api/contact', json=payload)
        self.assertEqual(response.status_code, 400)
        json_data = response.get_json()
        self.assertFalse(json_data['success'])

    # ── Admin Auth & Dashboard ──────────────────────────────────────────────────

    def test_admin_login_success(self):
        """Test admin login with correct credentials."""
        response = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'Admin@2026'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.data)

    def test_admin_login_invalid(self):
        """Test admin login with wrong credentials."""
        response = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'WrongPassword'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid username or password', response.data)

    def test_unauthenticated_dashboard_redirect(self):
        """Test accessing admin dashboard without login redirects to login page."""
        response = self.client.get('/admin/', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login', response.location)

    # ── Admin Project CRUD Operations ──────────────────────────────────────────

    def login_admin(self):
        """Helper to log in admin in test client."""
        self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'Admin@2026'
        })

    def test_add_project_flow(self):
        """Test adding a new project as admin."""
        self.login_admin()
        response = self.client.post('/admin/projects/add', data={
            'title': 'New Beta Project',
            'description': 'Beta project description',
            'technologies': 'React, Node',
            'date': 'July 2026',
            'github_url': '',
            'demo_url': '',
            'is_featured': '1',
            'status': 'Ongoing'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'New Beta Project', response.data)

    def test_edit_project_flow(self):
        """Test editing an existing project as admin."""
        self.login_admin()
        
        # Get ID of the seeded project
        with self.app.app_context():
            projects = get_all_projects()
            proj_id = projects[0]['id']

        response = self.client.post(f'/admin/projects/edit/{proj_id}', data={
            'title': 'Test Project Alpha Updated',
            'description': 'Updated description',
            'technologies': 'Python, Flask, SQLite',
            'date': 'May 2026',
            'github_url': 'https://github.com/updated',
            'demo_url': '',
            'is_featured': '',
            'status': 'Completed'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'updated successfully', response.data)
        
        with self.app.app_context():
            updated = get_project_by_id(proj_id)
            self.assertEqual(updated['title'], 'Test Project Alpha Updated')
            self.assertEqual(updated['is_featured'], 0)

    def test_toggle_featured_project(self):
        """Test toggling project featured state."""
        self.login_admin()
        with self.app.app_context():
            proj_id = get_all_projects()[0]['id']

        response = self.client.post(f'/admin/projects/feature/{proj_id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        with self.app.app_context():
            updated = get_project_by_id(proj_id)
            self.assertEqual(updated['is_featured'], 0)

    def test_delete_project_flow(self):
        """Test deleting a project as admin."""
        self.login_admin()
        with self.app.app_context():
            proj_id = get_all_projects()[0]['id']

        response = self.client.post(f'/admin/projects/delete/{proj_id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        with self.app.app_context():
            self.assertIsNone(get_project_by_id(proj_id))

    def test_admin_messages_view(self):
        """Test viewing and managing messages in admin area."""
        # Submit a message first
        self.client.post('/api/contact', json={
            'name': 'Message Sender',
            'email': 'sender@example.com',
            'message': 'Testing admin message inbox'
        })
        self.login_admin()

        response = self.client.get('/admin/messages')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Message Sender', response.data)

    def test_404_error_handler(self):
        """Test 404 custom error page."""
        response = self.client.get('/nonexistent-page-path')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'404', response.data)


if __name__ == '__main__':
    unittest.main()
