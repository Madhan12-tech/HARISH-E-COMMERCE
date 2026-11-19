
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Website settings
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "harish-development-secret-change-before-deployment"
    )

    # Database settings
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///harish.db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Image upload settings
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024

    UPLOAD_FOLDER = os.path.join(
        "static",
        "uploads"
    )

    ALLOWED_EXTENSIONS = {
        "png",
        "jpg",
        "jpeg",
        "webp"
    }

    # Razorpay payment settings
    RAZORPAY_KEY_ID = os.getenv(
        "RAZORPAY_KEY_ID",
        ""
    )

    RAZORPAY_KEY_SECRET = os.getenv(
        "RAZORPAY_KEY_SECRET",
        ""
    )

    # Store information
    STORE_NAME = "HARISH"
    STORE_TAGLINE = "SHOP EVERYTHING. ENJOY MORE."
    STORE_CURRENCY = "INR"
