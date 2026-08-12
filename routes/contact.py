import re
import os
import json
import urllib.request
import urllib.error
from flask import Blueprint, request, jsonify

from models.message import add_message

contact_bp = Blueprint('contact', __name__)

EMAIL_REGEX = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')

# Always send to this email address
OWNER_EMAIL = 'byreddypujith@gmail.com'


def send_email_via_resend(name, sender_email, message):
    """
    Send contact form notification via Resend API (https://resend.com).
    Free tier: 100 emails/day, 3000/month. Works on Vercel (no SMTP ports needed).
    Requires RESEND_API_KEY environment variable to be set.
    """
    api_key = os.environ.get('RESEND_API_KEY')
    if not api_key:
        print("[-] RESEND_API_KEY not set — skipping email notification")
        return False

    payload = {
        "from": "Portfolio Contact <onboarding@resend.dev>",
        "to": [OWNER_EMAIL],
        "reply_to": sender_email,
        "subject": f"Portfolio Contact from {name}",
        "html": f"""
        <div style="font-family: DM Sans, Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #1e160a; color: #fdf8f0; border-radius: 8px; overflow: hidden;">
          <div style="background: #d4943a; padding: 24px 32px;">
            <h1 style="margin: 0; font-size: 1.4rem; color: #110d06; font-family: Georgia, serif;">📬 New Portfolio Message</h1>
          </div>
          <div style="padding: 32px;">
            <p style="color: #c4b896; margin: 0 0 20px;">You received a new message from your portfolio website.</p>
            <table style="width: 100%; border-collapse: collapse;">
              <tr>
                <td style="padding: 10px 0; border-bottom: 1px solid rgba(212,148,58,0.2); color: #d4943a; font-size: 0.8rem; letter-spacing: 1px; text-transform: uppercase; width: 100px;">Name</td>
                <td style="padding: 10px 0; border-bottom: 1px solid rgba(212,148,58,0.2); color: #fdf8f0; font-weight: 600;">{name}</td>
              </tr>
              <tr>
                <td style="padding: 10px 0; border-bottom: 1px solid rgba(212,148,58,0.2); color: #d4943a; font-size: 0.8rem; letter-spacing: 1px; text-transform: uppercase;">Email</td>
                <td style="padding: 10px 0; border-bottom: 1px solid rgba(212,148,58,0.2);">
                  <a href="mailto:{sender_email}" style="color: #d4943a;">{sender_email}</a>
                </td>
              </tr>
            </table>
            <div style="margin-top: 24px;">
              <p style="color: #d4943a; font-size: 0.8rem; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 10px;">Message</p>
              <div style="background: rgba(212,148,58,0.08); border-left: 3px solid #d4943a; padding: 16px 20px; border-radius: 0 4px 4px 0; color: #fdf8f0; line-height: 1.7;">{message.replace(chr(10), '<br>')}</div>
            </div>
            <div style="margin-top: 28px; text-align: center;">
              <a href="mailto:{sender_email}" style="background: #d4943a; color: #110d06; padding: 12px 28px; border-radius: 4px; text-decoration: none; font-weight: 700; font-size: 0.85rem; letter-spacing: 1px; display: inline-block;">Reply to {name}</a>
            </div>
          </div>
          <div style="padding: 16px 32px; background: rgba(0,0,0,0.3); text-align: center; color: #7a5c30; font-size: 0.78rem;">
            Sent from your portfolio at full-stack-indol-tau.vercel.app
          </div>
        </div>
        """
    }

    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            'https://api.resend.com/emails',
            data=data,
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
            },
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            print(f"[+] Email sent via Resend: {result.get('id')}")
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"[-] Resend API error {e.code}: {body}")
        return False
    except Exception as e:
        print(f"[-] Email send failed: {e}")
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

        # Send email notification via Resend API
        send_email_via_resend(name, email, message)

        return jsonify({
            'success': True,
            'message': "Thanks for reaching out! I'll get back to you soon."
        }), 200
    except Exception as e:
        print(f"[-] Contact submission error: {e}")
        return jsonify({'success': False, 'errors': ['Server error. Please try again later.']}), 500
