from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import connection   #means from __init__.py import db connection
from flask_login import login_user, login_required, logout_user, current_user
from .queries import get_password, create_user
auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', "POST"])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password1')
        pass_hash = get_password(email)
        if check_password_hash(pass_hash, password):
            flash('Logged In!', category='success')
            return redirect(url_for('views.home'))
        else:
            flash("Email or Password does not match an existing user", category='error')
    return render_template("login.html", text="Testing")

@auth.route('/logout')
def logout():
    return "<p>Logout</p>"

@auth.route('/create_account', methods=['GET', "POST"])
def create_account():   
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be at least 4 characters', category='error')
        elif len(name) < 2:
            flash('Name must be at least 2 characters', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match', category='error')
        elif len(password2) < 7:
            flash('Password must be at least 7 characters', category='error')
        else:
            # create_user is a sql insert query, written in queries.py
            # need to create handling for if a user email already exists
            create_user(email=email, name=name, pass_hash=generate_password_hash(password1, method='pbkdf2:sha256'))
            return redirect(url_for('views.home'))
    return render_template("create_account.html")