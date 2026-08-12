from functools import wraps
# pyrefly: ignore [missing-import]
from flask import (Blueprint, render_template, request, redirect,
                   url_for, session, flash, jsonify)

from models.user import verify_password
from models.project import (get_all_projects, add_project, update_project,
                             delete_project, toggle_featured, get_project_by_id)
from models.message import get_all_messages, mark_as_read, delete_message, get_unread_count

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# ── Auth decorator ──────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Please log in to access the admin area.', 'warning')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated


# ── Login / Logout ──────────────────────────────────────────────────────────

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Username and password are required.', 'error')
            return render_template('admin/login.html')

        if verify_password(username, password):
            session.permanent = False
            session['admin_logged_in'] = True
            session['admin_username'] = username
            flash('Welcome back!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('admin/login.html')


@admin_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin.login'))


# ── Dashboard ────────────────────────────────────────────────────────────────

@admin_bp.route('/')
@login_required
def dashboard():
    projects = get_all_projects()
    messages = get_all_messages()
    unread = get_unread_count()
    return render_template('admin/dashboard.html',
                           projects=projects,
                           messages=messages,
                           unread=unread)


# ── Projects ─────────────────────────────────────────────────────────────────

@admin_bp.route('/projects/add', methods=['GET', 'POST'])
@login_required
def add_project_view():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        technologies = request.form.get('technologies', '').strip()
        date = request.form.get('date', '').strip()
        github_url = request.form.get('github_url', '').strip()
        demo_url = request.form.get('demo_url', '').strip()
        is_featured = 1 if request.form.get('is_featured') else 0
        status = request.form.get('status', 'Completed').strip()

        errors = []
        if not title:
            errors.append('Project title is required.')
        if not description:
            errors.append('Project description is required.')
        if not technologies:
            errors.append('Technologies are required.')
        if not date:
            errors.append('Date is required.')

        if errors:
            for e in errors:
                flash(e, 'error')
            return render_template('admin/project_form.html',
                                   form_data=request.form)

        add_project(title, description, technologies, date,
                    github_url, demo_url, is_featured, status)
        flash(f'Project "{title}" added successfully!', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/project_form.html', form_data={}, is_edit=False)


@admin_bp.route('/projects/edit/<int:project_id>', methods=['GET', 'POST'])
@login_required
def edit_project_view(project_id):
    project = get_project_by_id(project_id)
    if not project:
        flash('Project not found.', 'error')
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        technologies = request.form.get('technologies', '').strip()
        date = request.form.get('date', '').strip()
        github_url = request.form.get('github_url', '').strip()
        demo_url = request.form.get('demo_url', '').strip()
        is_featured = 1 if request.form.get('is_featured') else 0
        status = request.form.get('status', 'Completed').strip()

        errors = []
        if not title:
            errors.append('Project title is required.')
        if not description:
            errors.append('Project description is required.')
        if not technologies:
            errors.append('Technologies are required.')
        if not date:
            errors.append('Date is required.')

        if errors:
            for e in errors:
                flash(e, 'error')
            form_data = dict(request.form)
            form_data['id'] = project_id
            return render_template('admin/project_form.html',
                                   form_data=form_data, is_edit=True, project=project)

        update_project(project_id, title, description, technologies, date,
                       github_url, demo_url, is_featured, status)
        flash(f'Project "{title}" updated successfully!', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/project_form.html', form_data=project, is_edit=True, project=project)


@admin_bp.route('/projects/delete/<int:project_id>', methods=['POST'])
@login_required
def delete_project_view(project_id):
    project = get_project_by_id(project_id)
    if not project:
        flash('Project not found.', 'error')
        return redirect(url_for('admin.dashboard'))
    delete_project(project_id)
    flash(f'Project "{project["title"]}" deleted.', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/projects/feature/<int:project_id>', methods=['POST'])
@login_required
def feature_project(project_id):
    project = get_project_by_id(project_id)
    if not project:
        flash('Project not found.', 'error')
        return redirect(url_for('admin.dashboard'))
    toggle_featured(project_id)
    status_text = 'unfeatured' if project['is_featured'] else 'featured'
    flash(f'Project "{project["title"]}" is now {status_text}.', 'success')
    return redirect(url_for('admin.dashboard'))


# ── Messages ─────────────────────────────────────────────────────────────────

@admin_bp.route('/messages')
@login_required
def messages_view():
    messages = get_all_messages()
    # Mark all as read when viewed
    for msg in messages:
        if not msg['is_read']:
            mark_as_read(msg['id'])
    return render_template('admin/messages.html', messages=messages)


@admin_bp.route('/messages/delete/<int:message_id>', methods=['POST'])
@login_required
def delete_message_view(message_id):
    delete_message(message_id)
    flash('Message deleted.', 'success')
    return redirect(url_for('admin.messages_view'))
