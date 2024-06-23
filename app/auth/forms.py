from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s - %(lineno)d - %(levelname)s - %(message)s')

class LoginForm(FlaskForm):
    """Form for users to login."""
    username = StringField('Username', validators=[DataRequired(), Length(min=1, max=150)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    """Form for users to create a new account."""
    username = StringField('Username', validators=[DataRequired(), Length(min=1, max=150)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=150)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        """Validate that the username is not already in use."""
        user = User.query.filter_by(username=username.data).first()
        if user:
            logging.warning(f"Username already in use: {username.data}")
            raise ValidationError('Username is already in use. Please choose a different one.')

    def validate_email(self, email):
        """Validate that the email is not already in use and matches the correct format."""
        user = User.query.filter_by(email=email.data).first()
        if user:
            logging.warning(f"Email already in use: {email.data}")
            raise ValidationError('Email is already in use. Please use a different email address.')

        email_regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
        if not re.match(email_regex, email.data):
            logging.warning(f"Invalid email format: {email.data}")
            raise ValidationError('Invalid email format.')

    def validate_password(self, password):
        """Validate the password strength."""
        if len(password.data) < 8:
            logging.warning("Password too short")
            raise ValidationError('Password must be at least 8 characters long.')

        if not re.search(r"[A-Za-z]", password.data) or not re.search(r"[0-9]", password.data):
            logging.warning("Password too weak")
            raise ValidationError('Password must contain both letters and numbers.')
