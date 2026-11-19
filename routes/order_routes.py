
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort
)

from flask_login import login_required, current_user

from models import db, CartItem, Product, Order, OrderItem

from datetime import datetime
from uuid import uuid4


order_bp = Blueprint("orders", __name__)


# CHECKOUT PAGE
@order_bp.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():

    cart_items = CartItem.query.filter_by(
        user_id=current_user.id
    ).all()

    if not cart_items:
        flash("Your cart is empty.", "error")
        return redirect(url_for("cart.view_cart"))

    subtotal = sum(
        item.product.price * item.quantity
        for item in cart_items
    )

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        city = request.form.get("city", "").strip()
        state = request.form.get("state", "").strip()
        pincode = request.form.get("pincode", "").strip()

        payment_method = request.form.get(
            "payment_method", "COD"
        )

        if not all([name, phone, address, city, state, pincode]):
            flash("Please complete all delivery details.", "error")
            return redirect(url_for("orders.checkout"))

        if not phone.isdigit() or len(phone) != 10:
            flash("Enter a valid 10-digit mobile number.", "error")
            return redirect(url_for("orders.checkout"))

        if not pincode.isdigit() or len(pincode) != 6:
            flash("Enter a valid 6-digit PIN code.", "error")
            return redirect(url_for("orders.checkout"))

        if payment_method not in ["COD", "Online"]:
            flash("Invalid payment method.", "error")
            return redirect(url_for("orders.checkout"))

        # Verify stock before placing order
        for item in cart_items:
            product = Product.query.filter_by(
                id=item.product_id,
                active=True
            ).with_for_update().first()

            if not product or product.stock < item.quantity:
                flash(
                    f"Insufficient stock for {item.product.name}.",
                    "error"
                )
                return redirect(url_for("cart.view_cart"))

        delivery_address = (
            f"{name}, {address}, {city}, {state} - {pincode}"
        )

        try:
            order = Order(
                order_number="HARISH-" + uuid4().hex[:10].upper(),
                user_id=current_user.id,
                total_amount=subtotal,
                payment_method=payment_method,
                payment_status="Pending",
                order_status="Placed",
                delivery_address=delivery_address,
                phone=phone
            )

            db.session.add(order)
            db.session.flush()

            for item in cart_items:

                product = Product.query.filter_by(
                    id=item.product_id,
                    active=True
                ).with_for_update().first()

                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    product_name=product.name,
                    price=product.price,
                    quantity=item.quantity
                )

                db.session.add(order_item)

                # COD stock is deducted immediately.
                # Online stock is deducted after payment verification.
                if payment_method == "COD":
                    product.stock -= item.quantity

            if payment_method == "COD":
                order.payment_status = "Pending"

            db.session.commit()

            # Clear customer's cart
            CartItem.query.filter_by(
                user_id=current_user.id
            ).delete()

            db.session.commit()

            if payment_method == "Online":
                return redirect(
                    url_for(
                        "payment.create_payment",
                        order_id=order.id
                    )
                )

            return redirect(
                url_for(
                    "orders.order_success",
                    order_id=order.id
                )
            )

        except Exception:
            db.session.rollback()
            flash(
                "Unable to place your order. Please try again.",
                "error"
            )
            return redirect(url_for("orders.checkout"))

    return render_template(
        "checkout.html",
        cart_items=cart_items,
        subtotal=subtotal
    )


# ORDER SUCCESS
@order_bp.route("/order-success/<int:order_id>")
@login_required
def order_success(order_id):

    order = Order.query.filter_by(
        id=order_id,
        user_id=current_user.id
    ).first_or_404()

    return render_template(
        "order_success.html",
        order=order
    )


# CUSTOMER ORDER HISTORY
@order_bp.route("/my-orders")
@login_required
def my_orders():

    orders = Order.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Order.created_at.desc()
    ).all()

    return render_template(
        "orders.html",
        orders=orders
    )


# ORDER DETAILS
@order_bp.route("/order/<int:order_id>")
@login_required
def order_details(order_id):

    order = Order.query.filter_by(
        id=order_id,
        user_id=current_user.id
    ).first_or_404()

    return render_template(
        "order_details.html",
        order=order
    )


# TRACK ORDER
@order_bp.route("/track-order")
@login_required
def track_order():

    order_number = request.args.get(
        "order_number", ""
    ).strip()

    order = None

    if order_number:
        order = Order.query.filter_by(
            order_number=order_number,
            user_id=current_user.id
        ).first()

        if not order:
            flash("Order not found.", "error")

    return render_template(
        "track_order.html",
        order=order
    )
