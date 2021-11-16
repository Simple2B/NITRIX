from ..database import db
from sqlalchemy.orm import relationship
from app.utils import ModelMixin


class ResellerProduct(db.Model, ModelMixin):
    """Model matches reseller and product entities"""

    __tablename__ = "reseller_product"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    reseller_id = db.Column(db.Integer, db.ForeignKey("resellers.id"))
    months = db.Column(db.Integer)
    init_price = db.Column(db.Float)
    ext_price = db.Column(db.Float)
    ninja_product_id = db.Column(db.String(64))
    product = relationship("Product")
    reseller = relationship("Reseller", viewonly=True)
