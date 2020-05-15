from ..database import db
from .product import Product
from .reseller import Reseller


class ResellerProduct(db.Model):
    """Model matches reseller and product entities"""

    __tablename__ = "reseller_product"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"))
    reseller_id = db.Column(db.Integer, db.ForeignKey("reseller.id"))
    months = db.Column(db.Integer)
    price = db.Column(db.Float)
