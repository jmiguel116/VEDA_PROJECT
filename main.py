from flask import Blueprint, render_template, request, jsonify
import logging
import bleach
import re
from flask_mail import Mail, Message

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Homepage route."""
    logging.info("Rendering homepage.")
    return render_template('index.html', title="Homepage")

@bp.route('/about')
def about():
    """About page route."""
    logging.info("Rendering about page.")
    return render_template('about.html', title="About")

@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page route."""
    if request.method == 'POST':
        try:
            name = bleach.clean(request.form.get('name', ''))
            email = bleach.clean(request.form.get('email', ''))
            message = bleach.clean(request.form.get('message', ''))

            if not all([name, email, message]):
                logging.warning("Incomplete form submission.")
                return jsonify({'error': 'All fields are required.'}), 400

            if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
                logging.warning("Invalid email format.")
                return jsonify({'error': 'Invalid email address.'}), 400

            # Process the contact form (e.g., send email)
            send_contact_email(name, email, message)
            logging.info(f"Contact form submitted by {name} with email {email}.")
            return jsonify({'success': 'Message sent successfully.'})

        except Exception as e:
            logging.error(f"Error processing contact form: {e}")
            return jsonify({'error': 'An error occurred. Please try again later.'}), 500

    logging.info("Rendering contact page.")
    return render_template('contact.html', title="Contact")

def send_contact_email(name, email, message):
    """Sends a contact email."""
    try:
        msg = Message(subject="Contact Form Submission",
                      sender=email,
                      recipients=["your-email@example.com"],  # Replace with your email
                      body=f"Name: {name}\nEmail: {email}\nMessage: {message}")
        mail.send(msg)
        logging.info("Contact email sent successfully.")
    except Exception as e:
        logging.error(f"Error sending contact email: {e}")
        raise

# Assuming Flask-Mail is set up in your application factory
mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)
    
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)

    app.register_blueprint(bp)

    # Logging
    if not app.debug:
        if app.config.get('LOG_TO_STDOUT'):
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)
        else:
            file_handler = logging.FileHandler('app.log')
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Veda App startup')

    return app
