
from datetime import datetime
from app import db

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


# ==========================================
# USER MODEL
# ==========================================

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=False)

    password_hash = db.Column(db.String(255), nullable=False)

    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    pincode = db.Column(db.String(10))

    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    orders = db.relationship(
        "Order",
        back_populates="user",
        lazy=True
    )

    cart_items = db.relationship(
        "CartItem",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy=True
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"


# ==========================================
# CATEGORY MODEL
# ==========================================

class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False)

    description = db.Column(db.Text)
    image = db.Column(db.String(255))

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    products = db.relationship(
        "Product",
        back_populates="category",
        lazy=True
    )

    def __repr__(self):
        return f"<Category {self.name}>"


# ==========================================
# PRODUCT MODEL
# ==========================================

class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), unique=True, nullable=False)

    description = db.Column(db.Text)

    price = db.Column(db.Float, nullable=False, default=0)
    old_price = db.Column(db.Float, default=0)

    stock = db.Column(db.Integer, nullable=False, default=0)

    image = db.Column(db.String(255))
    image2 = db.Column(db.String(255))
    image3 = db.Column(db.String(255))

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id"),
        nullable=True
    )

    featured = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    category = db.relationship(
        "Category",
        back_populates="products"
    )

    cart_items = db.relationship(
        "CartItem",
        back_populates="product",
        lazy=True
    )

    order_items = db.relationship(
        "OrderItem",
        back_populates="product",
        lazy=True
    )

    def __repr__(self):
        return f"<Product {self.name}>"


# ==========================================
# CART MODEL
# ==========================================

class CartItem(db.Model):
    __tablename__ = "cart_items"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id"),
        nullable=False
    )

    quantity = db.Column(
        db.Integer,
        nullable=False,
        default=1
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user = db.relationship(
        "User",
        back_populates="cart_items"
    )

    product = db.relationship(
        "Product",
        back_populates="cart_items"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "product_id",
            name="unique_user_cart_product"
        ),
    )

    @property
    def subtotal(self):
        if self.product:
            return self.product.price * self.quantity
        return 0

    def __repr__(self):
        return f"<CartItem {self.id}>"


# ==========================================
# ORDER MODEL
# ==========================================

class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)

    order_number = db.Column(
        db.String(50),
        unique=True,
        nullable=False,
        index=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    total_amount = db.Column(
        db.Float,
        nullable=False,
        default=0
    )

    payment_method = db.Column(
        db.String(50),
        nullable=False,
        default="COD"
    )

    payment_status = db.Column(
        db.String(50),
        nullable=False,
        default="Pending"
    )

    order_status = db.Column(
        db.String(50),
        nullable=False,
        default="Pending"
    )

    delivery_address = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(20), nullable=False)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user = db.relationship(
        "User",
        back_populates="orders"
    )

    items = db.relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy=True
    )

    payments = db.relationship(
        "Payment",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy=True
    )

    def __repr__(self):
        return f"<Order {self.order_number}>"


# ==========================================
# ORDER ITEM MODEL
# ==========================================

class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("orders.id"),
        nullable=False
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id"),
        nullable=False
    )

    product_name = db.Column(
        db.String(200),
        nullable=False
    )

    quantity = db.Column(
        db.Integer,
        nullable=False,
        default=1
    )

    price = db.Column(
        db.Float,
        nullable=False,
        default=0
    )

    subtotal = db.Column(
        db.Float,
        nullable=False,
        default=0
    )

    order = db.relationship(
        "Order",
        back_populates="items"
    )

    product = db.relationship(
        "Product",
        back_populates="order_items"
    )

    def __repr__(self):
        return f"<OrderItem {self.id}>"


# ==========================================
# PAYMENT MODEL
# ==========================================

class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("orders.id"),
        nullable=False
    )

    gateway = db.Column(
        db.String(50),
        nullable=False,
        default="Razorpay"
    )

    # Stores the Razorpay order ID initially.
    # After successful verification, this can store
    # the Razorpay payment ID.
    transaction_id = db.Column(
        db.String(150),
        unique=True,
        nullable=True
    )

    amount = db.Column(
        db.Float,
        nullable=False,
        default=0
    )

    status = db.Column(
        db.String(50),
        nullable=False,
        default="Created"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    order = db.relationship(
        "Order",
        back_populates="payments"
    )

    def __repr__(self):
        return f"<Payment {self.id}>"
