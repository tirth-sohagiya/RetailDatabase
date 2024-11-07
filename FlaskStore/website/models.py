from . import db
from sqlalchemy.sql import func
from random import randint

class User(db.Model):
    uid = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(40), unique=True)
    name = db.Column(db.String(40))
    pass_hash = db.Column(db.String(15))

"""class Member(db.Model):
    uid = db.Column(db.Integer, db.ForeignKey('user.uid'))
    login_id = db.Column(db.String(20), primary_key=True)
    pass_hash = db.Column(db.String(60))"""

    