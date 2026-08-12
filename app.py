import os
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

from config import config
from models.db import close_db, init_db
from models.user import create_user, user_exists

# Load environment variables from .env file
load_dotenv()

csrf = CSRFProtect()


def create_app(config_name=None):
    """Application factory."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
        if config_name not in config:
            config_name = 'development'

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Extensions
    csrf.init_app(app)

    # Teardown
    app.teardown_appcontext(close_db)

    # Register blueprints
    from routes.main import main_bp
    from routes.contact import contact_bp
    from routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(contact_bp)
    app.register_blueprint(admin_bp)

    # Exempt the contact API from CSRF (uses JSON, not forms)
    csrf.exempt(contact_bp)

    # Exempt admin login from CSRF (no session exists yet, CSRF can't validate)
    from routes.admin import login as admin_login_view
    csrf.exempt(admin_login_view)

    # Handle CSRF errors gracefully (for other protected forms)
    from flask_wtf.csrf import CSRFError
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        from flask import redirect, url_for, flash
        flash('Session expired. Please refresh and try again.', 'error')
        return redirect(url_for('admin.login'))

    # Initialize database on first run
    with app.app_context():
        init_db(app)
        _seed_database(app)

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        from flask import render_template
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        from flask import render_template
        return render_template('errors/500.html'), 500

    return app


def _seed_database(app):
    """Seed default admin and sample projects on first run."""
    admin_username = app.config['ADMIN_USERNAME']
    admin_password = app.config['ADMIN_PASSWORD']

    # Create default admin user if not exists
    if not user_exists(admin_username):
        create_user(admin_username, admin_password)
        print(f"[+] Admin user '{admin_username}' created.")

    # Seed projects
    from models.project import get_all_projects, add_project
    if not get_all_projects():
        projects = [
            {
                'title': 'Silent Help',
                'description': 'Developing an ML model to classify user messages into Normal, Busy, and Distress states using feature engineering and Logistic Regression. Designed an alert mechanism to flag repeated distress signals, supporting early risk detection in digital communication.',
                'technologies': 'Python, Scikit-learn, Logistic Regression',
                'date': 'June 2026 - Present',
                'github_url': '#',
                'demo_url': '',
                'is_featured': 1,
                'status': 'Ongoing'
            },
            {
                'title': 'TasteScape – Restaurant Web Page',
                'description': 'Developed a front-end restaurant webpage with a structured and user-friendly interface. Designed responsive web components for presenting restaurant information and implemented interactive elements using HTML, CSS, and JavaScript.',
                'technologies': 'HTML, CSS, JavaScript',
                'date': 'March 2026',
                'github_url': '#',
                'demo_url': '',
                'is_featured': 1,
                'status': 'Completed'
            },
            {
                'title': 'Hotel Booking & Management System',
                'description': 'Developed a Java-based hotel management system for managing hotel details, room availability, ratings, locations, and pricing. Implemented sorting by name, rating, room availability, and price using Comparable and Java Collections. Added city-based filtering and room-booking functionality with availability validation.',
                'technologies': 'Java, OOP, Collections',
                'date': 'April 2025',
                'github_url': '#',
                'demo_url': '',
                'is_featured': 0,
                'status': 'Completed'
            },
        ]
        for p in projects:
            add_project(**p)
        print(f"[+] Seeded {len(projects)} projects.")


# Application entry point
app = create_app()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
