
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request
)

from flask_login import login_required, current_user

from models import db, Product, CartItem


cart_bp = Blueprint("cart", __name__)


# SHOPPING CART PAGE
@cart_bp.route("/cart")
@login_required
def view_cart():

    cart_items = CartItem.query.filter_by(
        user_id=current_user.id
    ).all()

    subtotal = sum(
        item.product.price * item.quantity
        for item in cart_items
    )

    return render_template(
        "cart.html",
        cart_items=cart_items,
        subtotal=subtotal,
        total=subtotal
    )


# ADD PRODUCT TO CART
@cart_bp.route("/cart/add/<int:product_id>", methods=["POST"])
@login_required
def add_to_cart(product_id):

    product = Product.query.filter_by(
        id=product_id,
        active=True
    ).first_or_404()

    if product.stock <= 0:
        flash("Sorry, this product is out of stock.", "error")
        return redirect(request.referrer or url_for("main.products"))

    try:
        quantity = int(request.form.get("quantity", 1))
    except (ValueError, TypeError):
        quantity = 1

    if quantity < 1:
        quantity = 1

    cart_item = CartItem.query.filter_by(
        user_id=current_user.id,
        product_id=product.id
    ).first()

    current_quantity = cart_item.quantity if cart_item else 0

    if current_quantity + quantity > product.stock:
        flash(
            f"Only {product.stock} units are available.",
            "error"
        )
        return redirect(request.referrer or url_for("main.products"))

    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(
            user_id=current_user.id,
            product_id=product.id,
            quantity=quantity
        )
        db.session.add(cart_item)

    db.session.commit()

    flash("Product added to your cart!", "success")

    return redirect(url_for("cart.view_cart"))


# UPDATE CART QUANTITY
@cart_bp.route("/cart/update/<int:item_id>", methods=["POST"])
@login_required
def update_cart(item_id):

    cart_item = CartItem.query.filter_by(
        id=item_id,
        user_id=current_user.id
    ).first_or_404()

    try:
        quantity = int(request.form.get("quantity", 1))
    except (ValueError, TypeError):
        flash("Invalid quantity.", "error")
        return redirect(url_for("cart.view_cart"))

    if quantity < 1:
        flash("Quantity must be at least 1.", "error")

    elif quantity > cart_item.product.stock:
        flash(
            f"Only {cart_item.product.stock} units are available.",
            "error"
        )

    else:
        cart_item.quantity = quantity
        db.session.commit()
        flash("Cart updated successfully.", "success")

    return redirect(url_for("cart.view_cart"))


# REMOVE PRODUCT FROM CART
@cart_bp.route("/cart/remove/<int:item_id>", methods=["POST"])
@login_required
def remove_from_cart(item_id):

    cart_item = CartItem.query.filter_by(
        id=item_id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(cart_item)
    db.session.commit()

    flash("Product removed from cart.", "success")

    return redirect(url_for("cart.view_cart"))


# CLEAR ENTIRE CART
@cart_bp.route("/cart/clear", methods=["POST"])
@login_required
def clear_cart():

    CartItem.query.filter_by(
        user_id=current_user.id
    ).delete()

    db.session.commit()

    flash("Your shopping cart is now empty.", "success")

    return redirect(url_for("cart.view_cart"))
