import re
from flask import Blueprint, request, jsonify

from models.message import add_message

contact_bp = Blueprint('contact', __name__)

EMAIL_REGEX = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')


@contact_bp.route('/api/contact', methods=['POST'])
def submit_contact():
    """Validate and store a contact form submission."""
    data = request.get_json(silent=True) or request.form

    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip()
    message = (data.get('message') or '').strip()

    errors = []

    if not name or len(name) < 2:
        errors.append('Name must be at least 2 characters.')
    if len(name) > 100:
        errors.append('Name is too long (max 100 characters).')

    if not email:
        errors.append('Email is required.')
    elif not EMAIL_REGEX.match(email):
        errors.append('Please enter a valid email address.')
    elif len(email) > 200:
        errors.append('Email is too long.')

    if not message or len(message) < 10:
        errors.append('Message must be at least 10 characters.')
    if len(message) > 2000:
        errors.append('Message is too long (max 2000 characters).')

    if errors:
        return jsonify({'success': False, 'errors': errors}), 400

    try:
        add_message(name, email, message)
        return jsonify({
            'success': True,
            'message': "Thanks for reaching out! I'll get back to you soon."
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'errors': ['Server error. Please try again later.']}), 500
