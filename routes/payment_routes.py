
# PAYMENT MODEL
class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("order.id"),
        nullable=False
    )

    gateway = db.Column(db.String(50))

    gateway_order_id = db.Column(db.String(150), unique=True)
    gateway_payment_id = db.Column(db.String(150))
    transaction_id = db.Column(db.String(150))

    amount = db.Column(db.Float, nullable=False)

    status = db.Column(
        db.String(50),
        default="Pending"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
