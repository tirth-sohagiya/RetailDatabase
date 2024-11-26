from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pymysql
from flask_login import LoginManager, current_user
import pymysql.cursors

db = SQLAlchemy()
DB_NAME = "SimpleStore"
# connection = pymysql.connect(host='localhost',
#                              user='root',
#                              password='root',
#                              database='test',
#                              charset='utf8mb4',
#                              cursorclass=pymysql.cursors.DictCursor)
login_manager = LoginManager()
                             
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'verysecurekey'
    app.config['SQLALCHEMY_DATABASE_URI'] =f'mysql+pymysql://admin:password@aws.cjwc228ggyr7.us-west-1.rds.amazonaws.com:3306/{DB_NAME}'
    db.init_app(app)
    login_manager.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    with app.app_context():
        db.create_all()

    login_manager.login_view = 'auth.login'
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    from .models import User

    # this doesn't work all the time
    @app.context_processor
    def inject_cart_count():
        from .queries import get_cart_count
        if current_user.is_authenticated:
            count = get_cart_count(current_user.id)
        else:
            count = get_cart_count(None)
        return dict(cart_count=count)

    return app
