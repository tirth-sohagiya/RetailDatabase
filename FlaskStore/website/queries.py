# This file contains SQLAlchemy ORM queries
from . import db
from .models import User, Product, Cart, Category, Transaction, Rating, Address, Order, Payment, OrderItem
from sqlalchemy import func 
from flask import session, flash # Using this to help track guest carts
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

def insert_address(address):
    # check if address already exists
    existing_address = Address.query.filter_by(street_address=address.street_address, city=address.city, state=address.state, zip=address.zip).first()
    if existing_address:
        return False
    if address.is_default:
            # Set all other addresses to non-default
            Address.query.filter_by(user_id=current_user.user_id, is_default=True).update({'is_default': False})
    db.session.add(address)
    db.session.commit()
    return True

def insert_payment(payment):
    # check if payment already exists
    existing_payment = Payment.query.filter_by(aes_card_num=payment.aes_card_num).first()
    if existing_payment:
        return False
    if payment.is_default:
        # Set all other payment methods to non-default
        Payment.query.filter_by(user_id=payment.user_id, is_default=True).update({'is_default': False})
    db.session.add(payment)
    db.session.commit()
    return True

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

def lock_cart(user_id):
    """Lock all cart items for a user during transaction processing"""
    try:
        cart_items = db.session.query(Cart).filter_by(user_id=user_id)\
            .with_for_update().all()
        
        for item in cart_items:
            item.is_locked = True
        
        db.session.commit()
        return True
            
    except Exception as e:
        print(f"Error locking cart: {str(e)}")
        return False

def unlock_cart(user_id):
    """Unlock all cart items for a user after transaction processing"""
    try:
        cart_items = db.session.query(Cart).filter_by(user_id=user_id)\
            .with_for_update().all()
        for item in cart_items:
            item.is_locked = False
        db.session.flush()
        return True
    except Exception as e:
        print(f"Error unlocking cart: {str(e)}")
        return False

def add_to_cart(user_id, product_id, quantity=1):
    """Add an item to cart. If user is logged in, use user_id, else use session"""

    # checking if cart is locked by a purchase
    if check_cart_lock(user_id):
        flash('Cart is currently locked for checkout processing: add_to_cart', category='error')
        return

    if quantity <= 0:
        raise ValueError("Items is out of stock")
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
    if check_cart_lock(user_id):
        flash('Cart is currently locked for checkout processing: get_cart_count', category='error')
        return
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
    return query.all()

def transfer_cart_signup(user_id):
    """Transfer guest cart to user cart on signup"""
    session_id = get_session_id()
    db.session.query(Cart).filter_by(session_id=get_session_id()).update({"user_id": user_id})
    db.session.commit()

def transfer_cart_login(user_id):
    """Transfer user cart to guest cart on login"""
    # Only transfer if the user has no current cart
    if db.session.query(Cart).filter_by(user_id=user_id).first() == None:
        db.session.query(Cart).filter_by(user_id=user_id).update({"session_id": get_session_id()})
        db.session.commit()

def clear_cart(user_id=None):
    if check_cart_lock(user_id):
        flash('Cart is currently locked for checkout processing: clear_cart', category='error')
        return
    if user_id:
         db.session.query(Cart).filter_by(user_id = user_id).delete()
    else:
        db.session.query(Cart).filter_by(session_id = get_session_id()).delete()
    db.session.commit()

def delete_from_cart(product_id, user_id=None):
    if check_cart_lock(user_id):
        flash('Cart is currently locked for checkout processing: delete_from_cart', category='error')
        return
    """ deletes product from cart, removes all quantity
        we currently don't allow users to update the quantity of an item in the cart"""
    print("In delete_from_cart. user_id:", user_id, "product_id:", product_id)
    if user_id:
        db.session.query(Cart).filter_by(user_id=user_id, product_id=product_id).delete()
    else:
        db.session.query(Cart).filter_by(session_id=get_session_id(), product_id=product_id).delete()
    db.session.commit()

# Using instead of a database trigger to batch update all product ratings
def set_all_product_ratings():
    product_ids = db.session.query(Product.product_id).all()
    for product in product_ids:
        rating = db.session.query(func.avg(Rating.stars)).filter_by(product_id=product.product_id).scalar()
        db.session.query(Product).filter_by(product_id=product.product_id).update({"rating": rating})
        db.session.commit()

def get_order_history(user_id):
    """ Gets all orders for a user
        This will implicitly get the order_items and transactions due to the relationships in models.py"""
    orders = db.session.query(Order)\
        .filter_by(user_id=user_id)\
        .order_by(Order.order_date.desc())\
        .all()
    return orders

# 
def create_order_transaction(user_id, payment_id, billing_address_id, shipping_address_id):
    """ creates the order, order_item, and transaction records for the order at checkout
        if the order is successfully created, it will return True"""

    # Lock the cart
    lock = lock_cart(user_id)
    print("lock:", lock)
    if not lock:
        flash('Unable to process order at this time', category='error')
        return False

    try:
        with db.session.begin():
            # Get cart items and lock the corresponding product rows
            cart_items = get_cart_items(user_id)
            if not cart_items:
                unlock_cart(user_id)
                flash('Your cart is empty', category='error')
                return False

            product_updates = {}  # Store updates to apply after validation
            
            # First pass: validate all quantities
            for item in cart_items:
                # Lock and get latest product data
                product = db.session.query(Product).filter_by(product_id=item.product_id)\
                    .with_for_update().first()
                
                # Check if enough stock
                if product.stock_quantity < item.quantity:
                    unlock_cart(user_id)
                    flash(f'Sorry, {product.name} only has {product.stock_quantity} items in stock', category='error')
                    return False
                
                # Store the update for later
                product_updates[product] = item.quantity
            
            # Second pass: apply all updates
            for product, quantity in product_updates.items():
                product.stock_quantity -= quantity
            
            # Create order and process transaction
            order = Order(user_id=user_id, address_id = shipping_address_id)
            db.session.add(order)
            db.session.flush()
            transaction = Transaction(order_id = order.order_id, payment_id = payment_id, billing_address_id = billing_address_id, amount = 0.00)

            # need to lock cart table here, we can't allow users to add items to the cart while an order is being created
            # pulling in all items from user's cart and adding them to the order
            cart_items = get_cart_items(user_id)
            for item in cart_items:
                order_item = OrderItem(order_id = order.order_id, product_id = item[4], quantity = item[3], unit_price = item[1])
                print("price:", order_item.unit_price)
                print("quantity:", order_item.quantity)
                db.session.add(order_item)
                transaction.amount += order_item.unit_price * order_item.quantity
            print("transaction:", transaction)
            print("order:", order)
            # add transaction
            db.session.add(transaction)
            
            # Clear cart and add transaction
            unlock_cart(user_id)
            clear_cart(user_id)  # This will also remove the locks
            
            return True
                
    except Exception as e:
        db.session.rollback()
        unlock_cart(user_id)  # Make sure to unlock on error
        raise e  # Re-raise to be caught by outer try-except

def check_cart_lock(user_id):
    """ returns true if cart is locked, false otherwise """
    try:
        locked_items = db.session.query(Cart).filter_by(user_id=user_id, is_locked=True).first()
        if locked_items:
            return True
        return False
    except Exception as e:
        print(f"Error checking cart lock: {str(e)}")
        return False

def search_products(search_term, sort_by='default', sort_order='asc'):
    """
    Search for products by name, description, or category.
    Only include products with a valid name, description, and image path.
    """
    try:
        query = Product.query.with_entities(
            Product,
            Category.category_id,
            Category.category_name.label('category_name')
        ).join(Category, Product.category_id == Category.category_id)\
        .filter(
            (Product.name.isnot(None)) & 
            (Product.name != '') & 
            (Product.description.isnot(None)) & 
            (Product.description != '') &
            (Product.img_path.isnot(None)) &  # Ensure img_path is not null
            (Product.img_path != '') &  # Ensure img_path is not empty
            (
                (Product.name.ilike(f'%{search_term}%')) |
                (Product.description.ilike(f'%{search_term}%')) |
                (Category.category_name.ilike(f'%{search_term}%'))
            )
        ).options(db.joinedload(Product.category))

        # Apply sorting
        if sort_by == 'price':
            query = query.order_by(Product.price.desc() if sort_order == 'desc' else Product.price)
        elif sort_by == 'rating':
            query = query.order_by(Product.rating.desc() if sort_order == 'desc' else Product.rating)

        return query.all()

    except Exception as e:
        print(f"Error in search_products: {str(e)}")
        return []