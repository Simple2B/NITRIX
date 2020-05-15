from ..database import db
from sqlalchemy_utils.types.choice import ChoiceType


class Product(db.Model):
    """Product entity"""

    TYPES = (
        ('active', 'Active'),
        ('not_active', 'Not active')
    )

    __tablename__ = 'product'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True, nullable=False)
    instance = db.Column(ChoiceType(TYPES), default='not_active')
 