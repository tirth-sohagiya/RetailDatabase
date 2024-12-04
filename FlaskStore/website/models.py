from . import db
from sqlalchemy.sql import func
from flask_login import UserMixin
from enum import Enum
from sqlalchemy import Enum as SQLAlchemyEnum
from datetime import datetime

## Some of the classes need editing

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(40), unique=True)
    first_name = db.Column(db.String(40), nullable=False)
    last_name = db.Column(db.String(40), nullable=False)
    pass_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    def get_id(self):
        return str(self.user_id)  # Flask-Login requires this to return a string

    @property
    def id(self):  # Add this property for Flask-Login compatibility
        return self.user_id

class Product(db.Model):
    __tablename__ = 'product'
    product_id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'), nullable=False)
    name = db.Column(db.String(40), nullable=False)
    img_path = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)

    # Add relationship to category for easier access
    category = db.relationship('Category', backref='products', lazy=True)

class Cart(db.Model):
    __tablename__ = 'cart'
    cart_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=False)
    session_id = db.Column(db.String(100))
    quantity = db.Column(db.Integer, nullable=False)
    added_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    is_locked = db.Column(db.Boolean, nullable=False, default=False)

class Category(db.Model):
    __tablename__ = 'category'
    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(40), nullable=False)

class Address(db.Model):
    __tablename__ = 'address'
    address_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    street_address = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(40), nullable=False)
    state = db.Column(db.String(40), nullable=False)
    zip = db.Column(db.String(10), nullable=False)
    country = db.Column(db.String(40), nullable=False, default='United States')
    is_default = db.Column(db.Boolean, nullable=False, default=False)

class Payment(db.Model):
    __tablename__ = 'payment'
    payment_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    payment_type = db.Column(db.String(10), nullable=False, default='credit')
    card_last_four = db.Column(db.String(4), nullable=False)
    aes_card_num = db.Column(db.String(300), nullable=False) # string of bits that needs to be converted into bytes and then decrypted
    expiration = db.Column(db.String(5), nullable=False)
    is_default = db.Column(db.Boolean, nullable=False, default=False)
    card_brand = db.Column(db.String(40), nullable=False)

class Rating(db.Model):
    __tablename__ = 'rating'
    rating_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    stars = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=False)
    rating_date = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)

class Order(db.Model):
    __tablename__ = 'customer_order'
    order_id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey('address.address_id'), nullable=False)
    order_date = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default="pending")
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True)
    transaction = db.relationship('Transaction', backref='order', lazy=True, uselist=False)
    user = db.relationship('User', backref='orders', lazy=True)
    address = db.relationship('Address', backref='orders', lazy=True)

    @property
    def total_amount(self):
        """Calculate total amount from order items"""
        return sum(item.unit_price * item.quantity for item in self.items)

    @staticmethod
    def generate_order_number():
        """Generate a unique order number"""
        import datetime
        prefix = datetime.datetime.now().strftime('ORD-%Y%m')
        # Get the last order number for this month
        last_order = Order.query.filter(
            Order.order_number.like(f'{prefix}%')
        ).order_by(Order.order_number.desc()).first()
        
        if last_order:
            # Extract the sequence number and increment
            seq = int(last_order.order_number.split('-')[-1]) + 1
        else:
            seq = 1
            
        return f'{prefix}-{seq:05d}'  # e.g., ORD-202401-00001

    def __init__(self, **kwargs):
        super(Order, self).__init__(**kwargs)
        if not self.order_number:
            self.order_number = self.generate_order_number()

class OrderItem(db.Model):
    __tablename__ = 'order_item'
    order_item_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('customer_order.order_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)  # Store the price at time of purchase

    # Add relationship to product for easy access to product details
    product = db.relationship('Product', backref='order_items', lazy=True)

class Transaction(db.Model):
    __tablename__ = 'order_transaction'
    transaction_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('customer_order.order_id'), nullable=False)
    payment_id = db.Column(db.Integer, db.ForeignKey('payment.payment_id'), nullable=False)
    billing_address_id = db.Column(db.Integer, db.ForeignKey('address.address_id'), nullable=False)
    external_transaction_id = db.Column(db.String(100), nullable=False)
    transaction_time = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    amount = db.Column(db.Float, nullable=False)  # Amount processed in this transaction

    # Relationships
    payment = db.relationship('Payment', backref='transactions', lazy=True)
    billing_address = db.relationship('Address', backref='transactions', lazy=True)