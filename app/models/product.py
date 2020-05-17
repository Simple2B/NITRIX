from ..database import db
from sqlalchemy_utils.types.choice import ChoiceType
from app.utils import ModelMixin


class Product(db.Model, ModelMixin):
    """Product entity"""

    TYPES = (
        ('active', 'Active'),
        ('not_active', 'Not active')
    )

    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True, nullable=False)
    status = db.Column(ChoiceType(TYPES), default='not_active')

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'status': 'active' if self.activated else 'not active'
        }

    @staticmethod
    def columns():
        return ['ID', 'Name', 'Status']