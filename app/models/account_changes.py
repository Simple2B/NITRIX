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
        imei = 'IMEI'
        product = 'Product'
        phone = 'Phone'
        reseller = 'Reseller'
        months = 'Months'
        activation_date = 'Activation date'
        created = 'Created'
        deleted = 'Deleted'

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    date = db.Column(db.DateTime, default=datetime.now)
    change_type = db.Column(Enum(ChangeType), default=ChangeType.name)
    value_str = db.Column(db.String(60), nullable=False)
    new_value_str = db.Column(db.String(60), nullable=True)
    account = relationship('Account', backref=db.backref("changes", lazy="dynamic"))
    user = relationship('User', backref=db.backref("changes", lazy="dynamic"))

    @property
    def message_by_account(self):
        if self.change_type == self.ChangeType.created:
            return f"[{self.date.strftime('%Y/%m/%d, %H:%M')}] Created by user {self.user.name}"
        elif self.change_type == self.ChangeType.deleted:
            return f"[{self.date.strftime('%Y/%m/%d, %H:%M')}] Deleted by user {self.user.name}"
        return f"[{self.date.strftime('%Y/%m/%d, %H:%M')}] User {self.user.name} changed {self.change_type.name} value from {self.value_str} to {self.new_value_str}"

    @property
    def message_by_user(self):
        if self.change_type == self.ChangeType.created:
            return f"[{self.date.strftime('%Y/%m/%d, %H:%M')}] Created account {self.account.name}"
        elif self.change_type == self.ChangeType.deleted:
            return f"[{self.date.strftime('%Y/%m/%d, %H:%M')}] Deleted account {self.account.name}"
        return f"[{self.date.strftime('%Y/%m/%d, %H:%M')}] Changed {self.change_type.value} value from {self.value_str} to {self.new_value_str} in account {self.account.name}"

    @classmethod
    def get_history(cls, account):
        changes_list = cls.query.filter(cls.account_id == account.id).order_by(cls.date.desc())
        return [change.message_by_account for change in changes_list]
