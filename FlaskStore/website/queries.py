# This file contains SQLAlchemy ORM queries
from . import db
from .models import User, Product, Cart, Category, Transaction, Rating, Address, Order, Payment, OrderItem
from sqlalchemy import func 
from flask import session # Using this to help track guest carts
import uuid # create unique guest ids
from functools import lru_cache
import time

def get_password(email):
    # Get password hash for a user by email
    user = User.query.filter_by(email=email).first()
    return user.pass_hash if user else None

def get_addresses(user_id):
    # Get all addresses for a user
    return Address.query.filter_by(user_id=user_id).all()

def get_payments(user_id):
    # Get all payments for a user
    return Payment.query.filter_by(user_id=user_id).all()

@lru_cache(maxsize=32)
def select_products(category, num, sort_by='default', sort_order='asc'):
    start = time.time()
    # Get products in a category, ordered by the specified field
    query = Product.query.with_entities(
        Product,
        Category.category_id,
        Category.category_name.label('category_name')
    ).join(Category, Product.category_id == Category.category_id)\
    .filter(Category.category_name.ilike(f'%{category}%'))\
    .options(db.joinedload(Product.category))

    # Apply sorting
    if sort_by == 'price':
        query = query.order_by(Product.price.desc() if sort_order == 'desc' else Product.price)
    elif sort_by == 'rating':
        query = query.order_by(Product.rating.desc() if sort_order == 'desc' else Product.rating)
    end = time.time()
    print(f"Product Select Query time: {end - start}")
    print(query.limit(num).all())
    return query.limit(num).all()

def search_products(search_term):
    # Search for products by name or description
    pass

def update_product_image_paths():
    """Update all product image paths to include category name as parent directory"""
    try:
        # Get all products with their categories
        products = db.session.query(Product, Category)\
            .join(Category, Product.category_id == Category.category_id)\
            .all()
        
        # Update each product's image path
        for product, category in products:
            # Only update if the category name isn't already in the path
            if not product.img_path.startswith(f"{category.category_name.lower()}/"):
                product.img_path = f"{category.category_name.lower()}/{product.img_path}"
        
        # Commit the changes
        db.session.commit()
        print(f"Successfully updated {len(products)} product image paths")
        return True
    except Exception as e:
        print(f"Error updating product image paths: {str(e)}")
        db.session.rollback()
        return False

def get_session_id():
    if 'cart_session_id' not in session:
        new_session_id = str(uuid.uuid4())
        # Find a unique session ID
        while True:
            if not Cart.query.filter_by(session_id=new_session_id).first():
                break
            new_session_id = str(uuid.uuid4())
        session['cart_session_id'] = new_session_id
    return session['cart_session_id']

def add_to_cart(user_id, product_id, quantity=1):
    """Add an item to cart. If user is logged in, use user_id, else use session"""
    if quantity <= 0:
        raise ValueError("Quantity must be greater than 0")
    if user_id:  # Logged in user
        cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id, session_id=None).first()
    else:  # Guest user
        session_id = get_session_id()
        cart_item = Cart.query.filter_by(session_id=session_id, product_id=product_id, user_id=None).first()

    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = Cart(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
            session_id=None if user_id else get_session_id()
        )
        db.session.add(cart_item)
    db.session.commit()

def get_cart_count(user_id=None):
    """Get number of items in cart"""
    if user_id:  # Logged in user
        result = db.session.query(func.sum(Cart.quantity))\
                          .filter_by(user_id=user_id).scalar()
    else:  # Guest user
        result = db.session.query(func.sum(Cart.quantity))\
                          .filter_by(session_id = get_session_id(), user_id=None).scalar()
    return result if result else 0

def get_cart_items(user_id=None):
    """Get all items in cart with product details"""
    query = db.session.query(
        Product.name,
        Product.price,
        Product.img_path,
        Cart.quantity,
        Product.product_id
    ).join(Cart, Cart.product_id == Product.product_id)

    if user_id:  # Logged in user
        query = query.filter(Cart.user_id == user_id, Cart.session_id == None)
    else:  # Guest user
        session_id = get_session_id()
        query = query.filter(Cart.session_id == session_id, Cart.user_id == None)
    print(query.all())
    return query.all()

def transfer_cart_signup(user_id):
    """Transfer guest cart to user cart on signup"""
    session_id = get_session_id()
    db.session.query(Cart).filter_by(session_id=get_session_id()).update({"user_id": user_id})
    db.session.commit()

def clear_cart(user_id=None):
    if user_id:
         db.session.query(Cart).filter_by(user_id = user_id).delete()
    else:
        db.session.query(Cart).filter_by(session_id = get_session_id()).delete()
    db.session.commit()

def delete_from_cart(product_id, user_id=None):
    print("In delete_from_cart. user_id:", user_id, "product_id:", product_id)
    if user_id:
        print("In user_id")
        db.session.query(Cart).filter_by(user_id=user_id, product_id=product_id).delete()
    else:
        print("In product_id")
        db.session.query(Cart).filter_by(session_id=get_session_id(), product_id=product_id).delete()
    db.session.commit()

# Using instead of a database trigger to batch update all product ratings
def set_all_product_ratings():
    # Select all product_ids
    product_ids = db.session.query(Product.product_id).all()
    for product in product_ids:
        rating = db.session.query(func.avg(Rating.stars)).filter_by(product_id=product.product_id).scalar()
        db.session.query(Product).filter_by(product_id=product.product_id).update({"rating": rating})
        db.session.commit()

def get_order_history(user_id):
    orders = Order.query.filter_by(user_id=user_id).order_by(Order.order_date.desc()).all()
    return orders

# creates the order, order_item, and transaction records for the order at checkout
def create_order_transaction(user_id, payment_id, billing_address_id, shipping_address_id):
    order = Order(user_id=user_id, address_id = shipping_address_id)
    # ToDo: create order number
    transaction = Transaction(order_id = order.order_id, payment_id = payment_id, billing_address_id = billing_address_id)
    # ToDo: create external transaction id

    # need to lock cart table here, we can't allow users to add items to the cart while an order is being created
    # pulling in all items from user's cart and adding them to the order
    cart_items = get_cart_items(user_id)
    for item in cart_items:
        order_item = OrderItem(order_id = order.order_id, product_id = item[4], quantity = item[3], unit_price = item[1])
        db.session.add(order_item)
        transaction.amount += order_item.unit_price * order_item.quantity
    # unlock cart table here
    # after the order items are added, clear the cart
    clear_cart(user_id)
    # commiting changes to the database
    db.session.add(transaction)
    db.session.add(order)
    db.session.commit()