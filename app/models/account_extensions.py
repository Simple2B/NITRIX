from ..database import db
from datetime import datetime
from app.utils import ModelMixin
from sqlalchemy.orm import relationship


class AccountExtension(db.Model, ModelMixin):
    """Model for extension account info"""

    __tablename__ = "account_extension"

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"))
    extension_date = db.Column(db.DateTime, default=datetime.now)
    end_date = db.Column(db.DateTime, default=datetime.now)
    months = db.Column(db.Integer)
    reseller_id = db.Column(db.Integer, db.ForeignKey("resellers.id"))
    reseller = relationship("Reseller")
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    product = relationship("Product")
    account = relationship("Account")
