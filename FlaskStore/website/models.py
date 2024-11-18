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

from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Product(db.Model):
    __tablename__ = 'product'
    pid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    price = db.Column(db.Float, nullable=False)
    img_path = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    def get_id(self):
        return str(self.pid)

class Cart(db.Model):
    __tablename__ = 'cart'
    uid = db.Column(db.Integer, db.ForeignKey('user.uid'), primary_key=True)
    pid = db.Column(db.Integer, db.ForeignKey('product.pid'), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)