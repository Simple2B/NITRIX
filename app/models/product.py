import enum
from ..database import db
from sqlalchemy import Enum
from app.utils import ModelMixin


class Product(db.Model, ModelMixin):
    """Product entity"""

    __tablename__ = 'products'

    class Status(enum.Enum):
        active = 'Active'
        not_active = 'Not active'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True, nullable=False)
    months = db.Column(db.Integer, default=3)
    status = db.Column(Enum(Status), default=Status.active)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'months': self.months,
            'status': self.status.value
        }

    @staticmethod
    def columns():
        return ['ID', 'Name', 'Available months', 'Status']
