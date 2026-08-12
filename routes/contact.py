import re
import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from flask import Blueprint, request, jsonify

from models.message import add_message

contact_bp = Blueprint('contact', __name__)

EMAIL_REGEX = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')


def send_email_notification(name, email, message):
    """Failsafe helper to email the contact submission to the admin if SMTP is configured."""
    smtp_host = os.environ.get('SMTP_HOST')
    smtp_port = os.environ.get('SMTP_PORT')
    smtp_user = os.environ.get('SMTP_USER')
    smtp_pass = os.environ.get('SMTP_PASSWORD')
    receiver = os.environ.get('RECEIVER_EMAIL') or smtp_user

    # If any required details are missing, skip forwarding (failsafe)
    if not all([smtp_host, smtp_port, smtp_user, smtp_pass]):
        return False

    try:
        msg_body = (
            f"You received a new message from your portfolio contact form:\n\n"
            f"Name: {name}\n"
            f"Email: {email}\n\n"
            f"Message:\n{message}\n"
        )
        msg = MIMEText(msg_body, 'plain', 'utf-8')
        msg['Subject'] = Header(f"Portfolio Contact: {name}", 'utf-8')
        msg['From'] = smtp_user
        msg['To'] = receiver

        port = int(smtp_port)
        if port == 465:
            server = smtplib.SMTP_SSL(smtp_host, port, timeout=10)
        else:
            server = smtplib.SMTP(smtp_host, port, timeout=10)
            server.starttls()

        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, [receiver], msg.as_string())
        server.quit()
        return True
    except Exception as e:
        # Log error to stderr/logs but don't crash
        print(f"[-] Email notification failed: {e}")
        return False


@contact_bp.route('/api/contact', methods=['POST'])
def submit_contact():
    """Validate, store, and forward a contact form submission."""
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
        
        # Trigger SMTP email sending (failsafe, won't block response on failure)
        send_email_notification(name, email, message)
        
        return jsonify({
            'success': True,
            'message': "Thanks for reaching out! I'll get back to you soon."
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'errors': ['Server error. Please try again later.']}), 500

