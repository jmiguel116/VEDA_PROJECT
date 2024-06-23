from flask import render_template, url_for, flash, redirect, request, send_from_directory, jsonify
from app import app, db
from app.forms import RegistrationForm, LoginForm, UploadForm
from app.models import User, File
from flask_login import login_user, current_user, logout_user, login_required
import os
from werkzeug.security import generate_password_hash, check_password_hash

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    elif form.errors:
        flash('Please fix the errors in the form', 'danger')
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    elif form.errors:
        flash('Please fix the errors in the form', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    form = UploadForm()
    if form.validate_on_submit():
        if form.file.data:
            file = form.file.data
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_record = File(filename=filename, author=current_user)
            db.session.add(file_record)
            db.session.commit()
            flash('File successfully uploaded', 'success')
    files = File.query.filter_by(author=current_user).all()
    for file in files:
        file.size = os.path.getsize(os.path.join(app.config['UPLOAD_FOLDER'], file.filename)) // 1024
    return render_template('dashboard.html', title='Dashboard', form=form, files=files)

@app.route("/download/<filename>")
@login_required
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/delete_file", methods=['DELETE'])
@login_required
def delete_file():
    filename = request.args.get('filename')
    file = File.query.filter_by(filename=filename, user_id=current_user.id).first()
    if file:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        db.session.delete(file)
        db.session.commit()
        return jsonify({'success': True}), 200
    return jsonify({'success': False}), 400

@app.route("/")
@app.route("/home")
def home():
    return render_template('index.html', title='Home')
