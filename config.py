
import os
from dotenv import load_dotenv

load_dotenv()


class Config:

    # Security
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "change-this-secret-before-deployment"
    )

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///harish.db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Image uploads
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024

    UPLOAD_FOLDER = os.path.join(
        "static", "uploads"
    )

    ALLOWED_EXTENSIONS = {
        "png", "jpg", "jpeg", "webp"
    }

    # Store branding
    STORE_NAME = "HARISH"
    STORE_TAGLINE = "SHOP EVERYTHING. ENJOY MORE."

    # Owner information
    OWNER_NAME = "Arish Kumar.G"
    OWNER_ROLE = "Founder & Owner"

    OWNER_VILLAGE = "Naranikuppam"
    OWNER_POST = "Kodipalli"
    OWNER_DISTRICT = "Krishnagiri"

    OWNER_PHONE = "9080836701"
    OWNER_EMAIL = "arishkumar6732@gmail.com"

    OWNER_IMAGE = "images/owner.jpg"

    # Currency
    STORE_CURRENCY = "INR"

    # Razorpay
    RAZORPAY_KEY_ID = os.getenv(
        "RAZORPAY_KEY_ID", ""
    )

    RAZORPAY_KEY_SECRET = os.getenv(
        "RAZORPAY_KEY_SECRET", ""
    )
