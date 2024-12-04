from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from .models import User, Address, Payment
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, login_manager
from flask_login import login_manager, login_user, login_required, logout_user, current_user
from .queries import get_password, get_order_history, transfer_cart_login, transfer_cart_signup


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
            transfer_cart_signup(new_user.user_id)
            flash('Account created!', category='success')
            return redirect(url_for('views.store_home'))
    return render_template("create_account.html")

@auth.route('/profile')
def profile():
    return render_template("profile.html", current_user=current_user)

@auth.route('/account/settings', methods=['GET', 'POST'])
@login_required
def account_settings():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_profile':
            # Update basic profile information
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            email = request.form.get('email')
            
            if email != current_user.email and User.query.filter_by(email=email).first():
                flash('Email already exists.', category='error')
                return redirect(url_for('auth.account_settings'))
            
            current_user.first_name = first_name
            current_user.last_name = last_name
            current_user.email = email
            db.session.commit()
            flash('Profile updated successfully!', category='success')
            
        elif action == 'change_password':
            # Change password
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            if not check_password_hash(current_user.pass_hash, current_password):
                flash('Current password is incorrect.', category='error')
            elif new_password != confirm_password:
                flash('New passwords do not match.', category='error')
            elif len(new_password) < 8:
                flash('Password must be at least 8 characters.', category='error')
            else:
                current_user.pass_hash = generate_password_hash(new_password)
                db.session.commit()
                flash('Password changed successfully!', category='success')
                
        elif action == 'add_address':
            # Add new address
            street = request.form.get('street')
            city = request.form.get('city')
            state = request.form.get('state')
            zip_code = request.form.get('zip_code')
            is_default = bool(request.form.get('is_default'))
            
            if is_default:
                # Set all other addresses to non-default
                Address.query.filter_by(user_id=current_user.user_id, is_default=True).update({'is_default': False})
            
            new_address = Address(
                user_id=current_user.user_id,
                street_address=street,
                city=city,
                state=state,
                zip=zip_code,
                is_default=is_default
            )
            db.session.add(new_address)
            db.session.commit()
            flash('Address added successfully!', category='success')
            
        elif action == 'add_payment':
            # Add new payment method
            card_number = request.form.get('card_number')
            expiration = request.form.get('expiration')
            card_brand = request.form.get('card_brand')
            is_default = bool(request.form.get('is_default'))
            
            if is_default:
                # Set all other payment methods to non-default
                Payment.query.filter_by(user_id=current_user.user_id, is_default=True).update({'is_default': False})
            
            new_payment = Payment(
                user_id=current_user.user_id,
                payment_type='credit',
                card_last_four=card_number[-4:],
                aes_card_num=card_number,  # In reality, this should be encrypted
                expiration=expiration,
                is_default=is_default,
                card_brand=card_brand
            )
            db.session.add(new_payment)
            db.session.commit()
            flash('Payment method added successfully!', category='success')
            
    # Get user's addresses and payment methods for display, should refactor to put queries in queries.py
    addresses = Address.query.filter_by(user_id=current_user.user_id).all()
    payment_methods = Payment.query.filter_by(user_id=current_user.user_id).all()
    
    return render_template(
        "account_settings.html",
        user=current_user,
        addresses=addresses,
        payment_methods=payment_methods
    )

@auth.route('/account/order-history', methods=['GET', 'POST'])
@login_required
def order_history():
    orders = get_order_history(current_user.id)
    return render_template("order_history.html", current_user=current_user, orders=orders)