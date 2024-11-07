from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .controller import Controller
import os
import pymysql
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "test"
controller = Controller(db)

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'imgoingtoseppuku'
    app.config['SQLALCHEMY_DATABASE_URI'] =f'mysql+pymysql://root:root@localhost/{DB_NAME}'
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User
    
    #login_manager = LoginManager()
    #login_manager.login_view = 'auth login'
    #login_manager.init_app(app)

    #@login_manager.user_loader
    #def load_user(id):
    #    return User.query.get(int(id))

    return app
