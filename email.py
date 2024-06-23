from flask_mail import Message
from app import mail, app
from flask import render_template
from itsdangerous import URLSafeTimedSerializer
import logging

# Configure logging
logging.basicConfig(filename='email.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the serializer for generating secure tokens
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

def send_email(subject, recipients, text_body, html_body):
    """
    Sends an email with the given subject, recipients, text body, and HTML body.

    Args:
        subject (str): The subject of the email.
        recipients (list): A list of email addresses to send the email to.
        text_body (str): The plain text body of the email.
        html_body (str): The HTML body of the email.
    """
    msg = Message(subject, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    try:
        mail.send(msg)
        logging.info(f"Email sent to {recipients} with subject: {subject}")
    except Exception as e:
        logging.error(f"Error sending email to {recipients}: {e}")

def send_password_reset_email(user):
    """
    Sends a password reset email to the given user.

    Args:
        user (User): The user object.
    """
    try:
        token = serializer.dumps(user.email)
        send_email(
            'Reset Your Password',
            [user.email],
            render_template('auth/email/reset_password.txt', user=user, token=token),
            render_template('auth/email/reset_password.html', user=user, token=token),
        )
        logging.info(f"Password reset email sent to {user.email}")
    except Exception as e:
        logging.error(f"Error sending password reset email to {user.email}: {e}")

def send_confirmation_email(user):
    """
    Sends a confirmation email to the given user.

    Args:
        user (User): The user object.
    """
    try:
        token = serializer.dumps(user.email)
        send_email(
            'Confirm Your Account',
            [user.email],
            render_template('auth/email/confirm.txt', user=user, token=token),
            render_template('auth/email/confirm.html', user=user, token=token),
        )
        logging.info(f"Confirmation email sent to {user.email}")
    except Exception as e:
        logging.error(f"Error sending confirmation email to {user.email}: {e}")
