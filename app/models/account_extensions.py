from ..database import db
from .account import Account
from datetime import datetime


class AccountExtension(db.Model):
    """Model for extension account info"""

    __tablename__ = "account_extension"

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey("account.id"))
    extension_date = db.Column(db.DateTime, default=datetime.now)
    months = db.Column(db.Integer)
