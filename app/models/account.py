from ..database import db
from .product import Product
from .reseller import Reseller
from datetime import datetime


class Account(db.Model):
    """Account entity"""

    __tablename__ = "account"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"))
    reseller_id = db.Column(db.Integer, db.ForeignKey("reseller.id"))
    sim = db.Column(db.String(20))
    comment = db.Column(db.String(200))
    activation_date = db.Column(db.DateTime, default=datetime.now)
    months = db.Column(db.Integer)
