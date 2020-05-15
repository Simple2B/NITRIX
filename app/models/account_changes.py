from ..database import db
from .account import Account
from datetime import datetime


class AccountChanges(db.Model):
    """Model for extension account info"""

    __tablename__ = "account_changes"

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey("account.id"))
    extension_date = db.Column(db.DateTime, default=datetime.now)
    name = db.Column(db.String(60), unique=True, nullable=False)
    sim = db.Column(db.String(20))
