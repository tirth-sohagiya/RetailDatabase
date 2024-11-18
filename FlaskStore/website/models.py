from . import db
from sqlalchemy.sql import func
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    
    uid = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(40), unique=True)
    name = db.Column(db.String(40), nullable=False)
    pass_hash = db.Column(db.String(15), nullable=False)
    def get_id(self):
        return str(self.uid)  # Flask-Login requires this to return a string

    @property
    def id(self):  # Add this property for Flask-Login compatibility
        return self.uid

class Product(db.Model):
    __tablename__ = 'product'
    pid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    price = db.Column(db.Float, nullable=False)
    img_path = db.Column(db.String(100), nullable=False)
    popularity = db.Column(db.Integer, nullable=False)
    def get_id(self):
        return str(self.pid)

class Cart(db.Model):
    __tablename__ = 'cart'
    cid = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('user.uid'))
    pid = db.Column(db.Integer, db.ForeignKey('product.pid'), nullable=False)
    session_id = db.Column(db.String(100))
    quantity = db.Column(db.Integer, nullable=False)