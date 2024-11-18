# This file contains SQLAlchemy ORM queries
from . import db
from .models import User, Product, Cart
from sqlalchemy import func 
from flask import session # Using this to help track guest carts
import uuid # create unique guest ids

def get_password(email):
    # Get password hash for a user by email
    user = User.query.filter_by(email=email).first()
    return user.pass_hash if user else None

def select_products(category, num):
    # Get products in a category, ordered by popularity
    return Product.query.filter_by()\
                       .order_by(Product.popularity.desc())\
                       .limit(num).all()

def get_session_id():
    if 'cart_session_id' not in session:
        session['cart_session_id'] = str(uuid.uuid4())
    return session['cart_session_id']

def add_to_cart(uid, pid, quantity=1):
    # Add or update item quantity in cart
    if uid:  # Logged in user
        cart_item = Cart.query.filter_by(uid=uid, pid=pid, session_id=None).first()
    else:  # Guest user
        session_id = get_session_id()
        cart_item = Cart.query.filter_by(session_id=session_id, pid=pid, uid=None).first()

    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = Cart(
            uid=uid,
            pid=pid,
            quantity=quantity,
            session_id=None if uid else get_session_id()
        )
        db.session.add(cart_item)
    db.session.commit()

def get_cart_count(uid=None):
    # Get total number of items in cart
    if uid:  # Logged in user
        result = db.session.query(func.sum(Cart.quantity))\
                          .filter_by(uid=uid, session_id=None).scalar()
    else:  # Guest user
        session_id = get_session_id()
        result = db.session.query(func.sum(Cart.quantity))\
                          .filter_by(session_id=session_id, uid=None).scalar()
    return result if result else 0

def get_cart_items(uid=None):
    # Get all items in cart with product details
    query = db.session.query(
        Product.name,
        Product.price,
        Product.img_path,
        Cart.quantity,
        Product.pid
    ).join(Cart, Cart.pid == Product.pid)

    if uid:  # Logged in user
        query = query.filter(Cart.uid == uid, Cart.session_id == None)
    else:  # Guest user
        session_id = get_session_id()
        query = query.filter(Cart.session_id == session_id, Cart.uid == None)

    return query.all()
