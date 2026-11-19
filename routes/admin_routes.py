
import os
from uuid import uuid4

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort,
    current_app
)

from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from models import db, User, Product, Category, Order


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# ADMIN SECURITY
@admin_bp.before_request
@login_required
def admin_required():

    if not current_user.is_admin:
        abort(403)


# IMAGE UPLOAD FUNCTION
def save_product_image(file):

    if not file or not file.filename:
        return None

    original_name = secure_filename(file.filename)

    if "." not in original_name:
        return None

    extension = original_name.rsplit(".", 1)[1].lower()

    allowed = current_app.config["ALLOWED_EXTENSIONS"]

    if extension not in allowed:
        return None

    filename = f"{uuid4().hex}.{extension}"

    upload_folder = current_app.config["UPLOAD_FOLDER"]

    os.makedirs(upload_folder, exist_ok=True)

    file.save(os.path.join(upload_folder, filename))

    return f"uploads/{filename}"


# ADMIN DASHBOARD
@admin_bp.route("/")
def dashboard():

    total_products = Product.query.count()
    total_customers = User.query.filter_by(is_admin=False).count()
    total_orders = Order.query.count()

    completed_sales = db.session.query(
        db.func.sum(Order.total_amount)
    ).filter_by(
        payment_status="Paid"
    ).scalar() or 0

    recent_orders = Order.query.order_by(
        Order.created_at.desc()
    ).limit(10).all()

    return render_template(
        "admin/dashboard.html",
        total_products=total_products,
        total_customers=total_customers,
        total_orders=total_orders,
        total_sales=completed_sales,
        recent_orders=recent_orders
    )


# VIEW PRODUCTS
@admin_bp.route("/products")
def products():

    products = Product.query.order_by(
        Product.created_at.desc()
    ).all()

    return render_template(
        "admin/products.html",
        products=products
    )


# ADD PRODUCT
@admin_bp.route("/products/add", methods=["GET", "POST"])
def add_product():

    categories = Category.query.all()

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()

        try:
            price = float(request.form.get("price", 0))
            old_price = request.form.get("old_price", "").strip()
            stock = int(request.form.get("stock", 0))
            category_id = int(request.form.get("category_id", 0))
        except (ValueError, TypeError):
            flash("Enter valid product details.", "error")
            return redirect(url_for("admin.add_product"))

        if not name or price <= 0 or stock < 0:
            flash("Check product name, price and stock.", "error")
            return redirect(url_for("admin.add_product"))

        category = db.session.get(Category, category_id)

        if not category:
            flash("Please select a valid category.", "error")
            return redirect(url_for("admin.add_product"))

        try:
            old_price = float(old_price) if old_price else None
        except ValueError:
            flash("Enter a valid old price.", "error")
            return redirect(url_for("admin.add_product"))

        if old_price is not None and old_price < price:
            flash("Old price must be greater than current price.", "error")
            return redirect(url_for("admin.add_product"))

        image = save_product_image(request.files.get("image"))

        if not image:
            flash("Please upload a valid product image.", "error")
            return redirect(url_for("admin.add_product"))

        slug = f"{uuid4().hex[:12]}"

        product = Product(
            name=name,
            slug=slug,
            description=description,
            price=price,
            old_price=old_price,
            stock=stock,
            category_id=category_id,
            image=image,
            featured=request.form.get("featured") == "on",
            active=True
        )

        db.session.add(product)
        db.session.commit()

        flash("Product added successfully!", "success")

        return redirect(url_for("admin.products"))

    return render_template(
        "admin/add_product.html",
        categories=categories
    )


# EDIT PRODUCT
@admin_bp.route("/products/edit/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):

    product = db.session.get(Product, product_id)

    if not product:
        abort(404)

    categories = Category.query.all()

    if request.method == "POST":

        try:
            price = float(request.form.get("price", 0))
            stock = int(request.form.get("stock", 0))
            category_id = int(request.form.get("category_id", 0))
            old_price_text = request.form.get("old_price", "").strip()
            old_price = float(old_price_text) if old_price_text else None
        except ValueError:
            flash("Invalid product values.", "error")
            return redirect(url_for("admin.edit_product", product_id=product.id))

        if price <= 0 or stock < 0:
            flash("Price must be positive and stock cannot be negative.", "error")
            return redirect(url_for("admin.edit_product", product_id=product.id))

        if old_price is not None and old_price < price:
            flash("Old price must be greater than current price.", "error")
            return redirect(url_for("admin.edit_product", product_id=product.id))

        if not db.session.get(Category, category_id):
            flash("Invalid category.", "error")
            return redirect(url_for("admin.edit_product", product_id=product.id))

        product.name = request.form.get("name", "").strip()
        product.description = request.form.get("description", "").strip()
        product.price = price
        product.old_price = old_price
        product.stock = stock
        product.category_id = category_id
        product.featured = request.form.get("featured") == "on"

        image = save_product_image(request.files.get("image"))

        if image:
            product.image = image

        product.active = request.form.get("active") == "on"

        db.session.commit()

        flash("Product updated successfully!", "success")

        return redirect(url_for("admin.products"))

    return render_template(
        "admin/edit_product.html",
        product=product,
        categories=categories
    )


# DELETE PRODUCT (SOFT DELETE)
@admin_bp.route("/products/delete/<int:product_id>", methods=["POST"])
def delete_product(product_id):

    product = db.session.get(Product, product_id)

    if not product:
        abort(404)

    product.active = False

    db.session.commit()

    flash("Product removed from the store.", "success")

    return redirect(url_for("admin.products"))


# MANAGE CATEGORIES
@admin_bp.route("/categories", methods=["GET", "POST"])
def categories():

    if request.method == "POST":

        name = request.form.get("name", "").strip()

        if not name:
            flash("Category name is required.", "error")

        elif Category.query.filter_by(name=name).first():
            flash("Category already exists.", "error")

        else:
            category = Category(name=name)

            db.session.add(category)
            db.session.commit()

            flash("Category created successfully!", "success")

    all_categories = Category.query.order_by(
        Category.name.asc()
    ).all()

    return render_template(
        "admin/categories.html",
        categories=all_categories
    )


# VIEW ALL ORDERS
@admin_bp.route("/orders")
def orders():

    all_orders = Order.query.order_by(
        Order.created_at.desc()
    ).all()

    return render_template(
        "admin/orders.html",
        orders=all_orders
    )


# UPDATE ORDER STATUS
@admin_bp.route("/orders/update/<int:order_id>", methods=["POST"])
def update_order(order_id):

    order = db.session.get(Order, order_id)

    if not order:
        abort(404)

    status = request.form.get("status")

    allowed_statuses = [
        "Placed",
        "Processing",
        "Shipped",
        "Out for Delivery",
        "Delivered",
        "Cancelled"
    ]

    if status not in allowed_statuses:
        flash("Invalid order status.", "error")
        return redirect(url_for("admin.orders"))

    if order.order_status == "Cancelled" or order.order_status == "Delivered":
        flash("This order can no longer be changed.", "error")
        return redirect(url_for("admin.orders"))

    if status == "Cancelled":
        if order.payment_status == "Paid":
            flash("Refund must be handled before cancelling a paid order.", "error")
            return redirect(url_for("admin.orders"))

        for item in order.items:
            product = db.session.get(Product, item.product_id)
            if product:
                product.stock += item.quantity

    order.order_status = status

    db.session.commit()

    flash("Order status updated successfully!", "success")

    return redirect(url_for("admin.orders"))


# VIEW CUSTOMERS
@admin_bp.route("/customers")
def customers():

    all_customers = User.query.filter_by(
        is_admin=False
    ).order_by(
        User.created_at.desc()
    ).all()

    return render_template(
        "admin/customers.html",
        customers=all_customers
    )
