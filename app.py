
import os

from flask import Flask
from flask_login import LoginManager

from config import Config
from models import db, User


# CREATE FLASK APPLICATION
app = Flask(__name__)

# LOAD CONFIGURATION
app.config.from_object(Config)


# CREATE REQUIRED FOLDERS
os.makedirs("instance", exist_ok=True)
os.makedirs("static/uploads", exist_ok=True)
os.makedirs("static/images", exist_ok=True)
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)


# INITIALIZE DATABASE
db.init_app(app)


# INITIALIZE LOGIN SYSTEM
login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "auth.login"

login_manager.login_message = "Please login to continue."


# LOAD CUSTOMER ACCOUNT
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# REGISTER WEBSITE MODULES
def register_routes():

    from routes.main_routes import main_bp
    from routes.auth_routes import auth_bp
    from routes.cart_routes import cart_bp
    from routes.order_routes import order_bp
    from routes.admin_routes import admin_bp
    from routes.payment_routes import payment_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(payment_bp)


# CREATE DATABASE TABLES
with app.app_context():
    db.create_all()


# APPLICATION START
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=os.environ.get("FLASK_DEBUG") == "1"
    )
