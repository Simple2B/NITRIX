import enum
from ..database import db
from sqlalchemy import Enum
from datetime import datetime
from sqlalchemy.orm import relationship
from app.utils import ModelMixin


class AccountChanges(db.Model, ModelMixin):
    """Model for extension account info"""

    __tablename__ = "account_changes"

    class ChangeType(enum.Enum):
        sim = 'SIM'
        name = 'Name'

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"))
    date = db.Column(db.DateTime, default=datetime.now)
    change_type = db.Column(Enum(ChangeType), default=ChangeType.name)
    value_str = db.Column(db.String(60), nullable=False)
    account = relationship('Account', backref=db.backref("changes", lazy="dynamic"))
