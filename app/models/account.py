from ..database import db
from datetime import datetime
from app.utils import ModelMixin


class Account(db.Model, ModelMixin):
    """Account entity"""

    __tablename__ = "accounts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    reseller_id = db.Column(db.Integer, db.ForeignKey("resellers.id"))
    sim = db.Column(db.String(20))
    comment = db.Column(db.String(200))
    activation_date = db.Column(db.DateTime, default=datetime.now)
    months = db.Column(db.Integer)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'product': self.product.name,
            'reseller': self.reseller.name,
            'sim': self.sim,
            'activation_date': self.activation_date,
            'months': self.months
        }

    @staticmethod
    def columns():
        return ['ID', 'Name', 'Product', 'Re-seller', 'SIM', 'Activation Date', 'Months']