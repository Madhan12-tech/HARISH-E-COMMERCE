
import os
from datetime import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

# --------------------------------------------------
# INITIALIZE EXTENSIONS
# --------------------------------------------------

db = SQLAlchemy()
login_manager = LoginManager()

login_manager.login_view = "auth.login"
login_manager.login_message = "Please login to continue."
login_manager.login_message_category = "info"


# --------------------------------------------------
# APPLICATION FACTORY
# --------------------------------------------------

def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Create required folders
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs("static/images", exist_ok=True)
    os.makedirs("instance", exist_ok=True)

    # --------------------------------------------------
    # IMPORT MODELS
    # --------------------------------------------------

    from models import User

    # --------------------------------------------------
    # LOGIN USER LOADER
    # --------------------------------------------------

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return db.session.get(User, int(user_id))
        except (ValueError, TypeError):
            return None

    # --------------------------------------------------
    # REGISTER BLUEPRINTS
    # --------------------------------------------------

    from routes.main_routes import main_bp
    from routes.auth_routes import auth_bp
    from routes.cart_routes import cart_bp
    from routes.order_routes import order_bp
    from routes.payment_routes import payment_bp
    from routes.admin_routes import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(admin_bp)

    # --------------------------------------------------
    # GLOBAL TEMPLATE DATA
    # --------------------------------------------------

    @app.context_processor
    def inject_global_data():
        return {
            "now": datetime.now(),
            "store_name": app.config["STORE_NAME"],
            "store_tagline": app.config["STORE_TAGLINE"]
        }

    # --------------------------------------------------
    # ERROR HANDLERS
    # --------------------------------------------------

    @app.errorhandler(404)
    def page_not_found(error):
        return "Page not found. Please check the URL.", 404

    @app.errorhandler(500)
    def internal_server_error(error):
        db.session.rollback()
        return "Something went wrong. Please try again later.", 500

    # --------------------------------------------------
    # DATABASE INITIALIZATION
    # --------------------------------------------------

    with app.app_context():
        db.create_all()

    return app


# --------------------------------------------------
# CREATE APPLICATION
# --------------------------------------------------

app = create_app()


# --------------------------------------------------
# LOCAL DEVELOPMENT
# --------------------------------------------------

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    )
