
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


# CUSTOMER MODEL
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(20))

    password_hash = db.Column(db.String(255), nullable=False)

    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    pincode = db.Column(db.String(10))

    is_admin = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    orders = db.relationship("Order", backref="customer", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# CATEGORY MODEL
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    image = db.Column(db.String(255))

    products = db.relationship("Product", backref="category", lazy=True)


# PRODUCT MODEL
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), unique=True)

    description = db.Column(db.Text)

    price = db.Column(db.Float, nullable=False)
    old_price = db.Column(db.Float)

    stock = db.Column(db.Integer, default=0)

    image = db.Column(db.String(255))
    image2 = db.Column(db.String(255))
    image3 = db.Column(db.String(255))

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("category.id")
    )

    featured = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# SHOPPING CART MODEL
class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("product.id"),
        nullable=False
    )

    quantity = db.Column(db.Integer, default=1)

    product = db.relationship("Product")


# ORDER MODEL
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    order_number = db.Column(db.String(50), unique=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    total_amount = db.Column(db.Float, nullable=False)

    payment_method = db.Column(db.String(50))
    payment_status = db.Column(
        db.String(50),
        default="Pending"
    )

    order_status = db.Column(
        db.String(50),
        default="Placed"
    )

    delivery_address = db.Column(db.Text)
    phone = db.Column(db.String(20))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship(
        "OrderItem",
        backref="order",
        lazy=True,
        cascade="all, delete-orphan"
    )


# ORDER ITEMS MODEL
class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("order.id"),
        nullable=False
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("product.id"),
        nullable=False
    )

    product_name = db.Column(db.String(200))
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)


# PAYMENT MODEL
class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("order.id"),
        nullable=False
    )

    gateway = db.Column(db.String(50))
    transaction_id = db.Column(db.String(150))

    amount = db.Column(db.Float, nullable=False)

    status = db.Column(
        db.String(50),
        default="Pending"
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
