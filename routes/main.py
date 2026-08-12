from flask import Blueprint, jsonify, render_template
from models.project import get_all_projects

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Serve the main portfolio page."""
    return render_template('index.html')


@main_bp.route('/api/projects')
def api_projects():
    """Return all projects as JSON for the frontend."""
    projects = get_all_projects()
    return jsonify({'projects': projects, 'count': len(projects)})
