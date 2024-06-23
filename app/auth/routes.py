from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User, db
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm
from app.auth.email import send_password_reset_email, send_confirmation_email
import logging
from itsdangerous import URLSafeTimedSerializer

auth_blueprint = Blueprint('auth', __name__)

# Configure logging
logging.basicConfig(filename='auth.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Token serializer for generating and verifying tokens
serializer = URLSafeTimedSerializer('SECRET_KEY')

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle login requests and validate user credentials.
    Redirects to the main page if the user is already logged in.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not check_password_hash(user.password_hash, form.password.data):
            logging.warning("Invalid username or password")
            flash('Invalid username or password.', 'danger')
        else:
            login_user(user, remember=form.remember_me.data)
            logging.info(f"User {user.username} logged in successfully")
            flash('Logged in successfully.', 'success')
            return redirect(url_for('main.index'))
    return render_template('auth/login.html', form=form)

@auth_blueprint.route('/logout')
@login_required
def logout():
    """
    Handle logout requests.
    Logs the user out and redirects to the login page.
    """
    logout_user()
    flash('You have been logged out.', 'success')
    logging.info("User logged out successfully")
    return redirect(url_for('auth.login'))

@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle registration requests.
    Registers a new user if the form is validated.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        send_confirmation_email(new_user)
        flash('Registration successful. A confirmation email has been sent.', 'success')
        logging.info(f"New user {new_user.username} registered successfully")
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth_blueprint.route('/confirm/<token>')
def confirm_email(token):
    """
    Confirm user's email address.
    """
    try:
        email = serializer.loads(token, max_age=3600)
    except Exception as e:
        logging.error(f"Invalid or expired token: {e}")
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(email=email).first_or_404()
    if user.email_confirmed:
        flash('Account already confirmed. Please login.', 'success')
    else:
        user.email_confirmed = True
        db.session.commit()
        flash('You have confirmed your account. Thanks!', 'success')
    return redirect(url_for('auth.login'))

@auth_blueprint.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    """
    Request password reset.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            flash('Check your email for the instructions to reset your password', 'info')
            logging.info(f"Password reset email sent to {user.email}")
        else:
            flash('No account found with that email address.', 'danger')
    return render_template('auth/reset_password_request.html', form=form)

@auth_blueprint.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    Reset password using the provided token.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    try:
        email = serializer.loads(token, max_age=3600)
    except Exception as e:
        logging.error(f"Invalid or expired token: {e}")
        flash('The password reset link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.reset_password_request'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=email).first_or_404()
        user.password_hash = generate_password_hash(form.password.data)
        db.session.commit()
        flash('Your password has been reset.', 'success')
        logging.info(f"User {user.username} has reset their password")
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)

