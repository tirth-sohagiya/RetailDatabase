from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, login_manager   #means from __init__.py import db connection
from flask_login import login_manager, login_user, login_required, logout_user, current_user
from .queries import get_password


auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', "POST"])
def login():
    if request.method == 'POST':
        # Get form data
        email = request.form.get('email')
        password = request.form.get('password1')
        pass_hash = get_password(email)

        # Throws an alert to user that email returned null
        # check_password_hash throws an error if it receives a none type
        if not pass_hash:
            flash("Email or Password does not match an existing user", category='error')
            return render_template("login.html", current_user=current_user)

        # Checks if password is correct
        if check_password_hash(pass_hash, password):
            flash('Logged In!', category='success')
            login_user(User.query.filter_by(email=email).first(), remember=True)
            return redirect(url_for('views.store_home'))
        else:
            flash("Email or Password does not match an existing user", category='error')
    return render_template("login.html", current_user=current_user)

@auth.route('/logout')
def logout():
    # flask function that removes the reference to the current user
    logout_user()
    return redirect(url_for('views.store_home'))

@auth.route('/create_account', methods=['GET', "POST"])
def create_account():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be at least 4 characters', category='error')
        elif len(first_name) < 2 or len(last_name) < 2:
            flash('Name must be at least 2 characters', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match', category='error')
        elif len(password2) < 7:
            flash('Password must be at least 7 characters', category='error')
        else:
            # need to create handling for if a user email already exists
            new_user = User(email=email, first_name=first_name, last_name=last_name, pass_hash=generate_password_hash(password1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            return redirect(url_for('views.store_home'))
    return render_template("create_account.html")

@auth.route('/profile')
def profile():
    return render_template("profile.html", current_user=current_user)