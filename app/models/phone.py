import enum
from ..database import db
from sqlalchemy import Enum
from app.utils import ModelMixin


class Phone(db.Model, ModelMixin):
    """phone entity"""

    __tablename__ = 'phones'

    class Status(enum.Enum):
        active = 'Active'
        not_active = 'Not active'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    status = db.Column(Enum(Status), default=Status.active)
    price = db.Column(db.Float, default=0.00)
    deleted = db.Column(db.Boolean, default=False)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'status': self.status.value
        }

    @staticmethod
    def columns():
        return ['ID', 'Name', 'Price', 'Status']
