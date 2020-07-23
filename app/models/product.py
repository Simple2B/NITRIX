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
    status = db.Column(Enum(Status), default=Status.active)
    deleted = db.Column(db.Boolean, default=False)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status.value
        }

    @staticmethod
    def columns():
        return ['ID', 'Name', 'Status']


@classmethod
def get_ordered_by_name_desc(cls):
    return cls.query.filter(cls.deleted == False).order_by(cls.name).all()  # noqa E712
