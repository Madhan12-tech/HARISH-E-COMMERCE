
import razorpay

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    current_app,
    abort
)

from flask_login import login_required, current_user

from models import db, Order, Payment, Product


payment_bp = Blueprint(
    "payment",
    __name__,
    url_prefix="/payment"
)


# CREATE RAZORPAY CLIENT
def get_razorpay_client():

    key_id = current_app.config["RAZORPAY_KEY_ID"]
    key_secret = current_app.config["RAZORPAY_KEY_SECRET"]

    if not key_id or not key_secret:
        return None

    return razorpay.Client(
        auth=(key_id, key_secret)
    )


# CREATE ONLINE PAYMENT
@payment_bp.route("/create/<int:order_id>", methods=["GET"])
@login_required
def create_payment(order_id):

    order = Order.query.filter_by(
        id=order_id,
        user_id=current_user.id
    ).first_or_404()

    if order.payment_method != "Online":
        abort(403)

    if order.payment_status == "Paid":
        return redirect(
            url_for(
                "orders.order_success",
                order_id=order.id
            )
        )

    if order.order_status == "Cancelled":
        flash("This order has been cancelled.", "error")
        return redirect(url_for("orders.my_orders"))

    client = get_razorpay_client()

    if not client:
        flash("Online payment is not configured yet.", "error")
        return redirect(url_for("orders.my_orders"))

    payment = Payment.query.filter_by(
        order_id=order.id,
        status="Pending"
    ).order_by(Payment.id.desc()).first()

    try:

        if payment and payment.gateway_order_id:
            gateway_order_id = payment.gateway_order_id

        else:

            razorpay_order = client.order.create({
                "amount": int(round(order.total_amount * 100)),
                "currency": "INR",
                "receipt": order.order_number,
                "notes": {
                    "harish_order": order.order_number
                }
            })

            gateway_order_id = razorpay_order["id"]

            payment = Payment(
                order_id=order.id,
                gateway="Razorpay",
                gateway_order_id=gateway_order_id,
                amount=order.total_amount,
                status="Pending"
            )

            db.session.add(payment)
            db.session.commit()

        return render_template(
            "payment.html",
            order=order,
            payment=payment,
            razorpay_key=current_app.config["RAZORPAY_KEY_ID"],
            gateway_order_id=gateway_order_id
        )

    except Exception:
        db.session.rollback()

        current_app.logger.exception(
            "Razorpay order creation failed"
        )

        flash(
            "Unable to start payment. Please try again.",
            "error"
        )

        return redirect(url_for("orders.my_orders"))


# VERIFY ONLINE PAYMENT
@payment_bp.route("/verify", methods=["POST"])
@login_required
def verify_payment():

    order_id = request.form.get("order_id")

    order = Order.query.filter_by(
        id=order_id,
        user_id=current_user.id
    ).first_or_404()

    payment = Payment.query.filter_by(
        order_id=order.id,
        status="Pending"
    ).order_by(Payment.id.desc()).first()

    if not payment:
        flash("Payment record not found.", "error")
        return redirect(url_for("orders.my_orders"))

    client = get_razorpay_client()

    if not client:
        flash("Payment gateway is unavailable.", "error")
        return redirect(url_for("orders.my_orders"))

    payment_id = request.form.get("razorpay_payment_id")
    gateway_order_id = request.form.get("razorpay_order_id")
    signature = request.form.get("razorpay_signature")

    if (
        not payment_id
        or not gateway_order_id
        or not signature
        or gateway_order_id != payment.gateway_order_id
    ):
        flash("Invalid payment details.", "error")
        return redirect(
            url_for("payment.create_payment", order_id=order.id)
        )

    try:

        client.utility.verify_payment_signature({
            "razorpay_order_id": gateway_order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature
        })

        # Verify gateway payment status
        gateway_payment = client.payment.fetch(payment_id)

        if gateway_payment.get("status") != "captured":
            flash(
                "Payment has not been captured yet. Please try again.",
                "error"
            )
            return redirect(
                url_for("payment.create_payment", order_id=order.id)
            )

        if int(gateway_payment.get("amount", 0)) != int(
            round(order.total_amount * 100)
        ):
            abort(400)

        if gateway_payment.get("order_id") != gateway_order_id:
            abort(400)

        # Lock and recheck the order
        order = Order.query.filter_by(
            id=order.id,
            user_id=current_user.id
        ).with_for_update().first_or_404()

        payment = Payment.query.filter_by(
            id=payment.id,
            order_id=order.id
        ).first_or_404()

        if order.payment_status == "Paid":
            return redirect(
                url_for(
                    "orders.order_success",
                    order_id=order.id
                )
            )

        if order.order_status == "Cancelled":
            flash("This order is cancelled. Contact support for payment assistance.", "error")
            return redirect(url_for("orders.my_orders"))

        if payment.status != "Pending":
            flash("Payment is already processed.", "error")
            return redirect(url_for("orders.my_orders"))

        # Check stock before deducting
        for item in order.items:

            product = Product.query.filter_by(
                id=item.product_id,
                active=True
            ).with_for_update().first()

            if not product or product.stock < item.quantity:
                flash(
                    "Stock unavailable. Contact support for payment assistance.",
                    "error"
                )
                return redirect(url_for("orders.my_orders"))

        # Deduct stock exactly once
        for item in order.items:

            product = db.session.get(
                Product,
                item.product_id
            )

            product.stock -= item.quantity

        payment.gateway_payment_id = payment_id
        payment.transaction_id = payment_id
        payment.status = "Paid"

        order.payment_status = "Paid"

        db.session.commit()

        flash(
            "Payment successful! Thank you for shopping with HARISH.",
            "success"
        )

        return redirect(
            url_for(
                "orders.order_success",
                order_id=order.id
            )
        )

    except razorpay.errors.SignatureVerificationError:

        flash("Payment verification failed.", "error")

        return redirect(
            url_for("payment.create_payment", order_id=order.id)
        )

    except Exception:

        db.session.rollback()

        current_app.logger.exception(
            "Payment verification failed"
        )

        flash(
            "Unable to verify payment. Please contact support.",
            "error"
        )

        return redirect(url_for("orders.my_orders"))


# PAYMENT FAILURE PAGE
@payment_bp.route("/failed/<int:order_id>")
@login_required
def payment_failed(order_id):

    order = Order.query.filter_by(
        id=order_id,
        user_id=current_user.id
    ).first_or_404()

    flash(
        "Payment was unsuccessful. You can retry from your orders.",
        "error"
    )

    return redirect(
        url_for("payment.create_payment", order_id=order.id)
    )
