from datetime import datetime
import enum
from sqlalchemy import Enum
from sqlalchemy.orm import relationship

from ..database import db
from app.utils import ModelMixin


def get_current_user_id():
    from flask_login import current_user

    return current_user.id


class HistoryChange(db.Model, ModelMixin):
    """Model for extension account info"""

    __tablename__ = "history_changes"

    class EditType(enum.Enum):
        creation_account = "creation_account"
        deletion_account = "deletion_account"
        changes_account = "changes_account"
        extension_account_new = "extension_account_new"
        extensions_account_change = "extensions_account_change"
        extensions_account_delete = "extensions_account_delete"
        creation_reseller = "creation_reseller"
        deletion_reseller = "deletion_reseller"
        changes_reseller = "changes_reseller"
        creation_product = "creation_product"
        deletion_product = "deletion_product"
        changes_product = "changes_product"

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer)  # acc | res | prod id
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), default=get_current_user_id
    )
    date = db.Column(db.DateTime, default=datetime.now)
    change_type = db.Column(Enum(EditType))
    value_name = db.Column(db.String(64))
    before_value_str = db.Column(db.String(64))
    after_value_str = db.Column(db.String(64))
    synced = db.Column(db.Boolean, default=False)
    user = relationship("User", viewonly=True)

    @property
    def message_by_account(self):
        if self.change_type == self.EditType.creation_account:
            return f"[{self.date.strftime('%Y/%m/%d, %H:%M')}] Created by user [{self.user.name}]"
        if self.change_type == self.EditType.deletion_account:
            return f"[{self.date.strftime('%Y/%m/%d, %H:%M')}] Deleted by user [{self.user.name}]"
        return "[{}] User [{}] changed [{}] value from [{}] to [{}]".format(
            self.date.strftime("%Y/%m/%d, %H:%M:%S"),
            self.user.name,
            self.value_name,
            self.before_value_str,
            self.after_value_str,
        )

    @classmethod
    def get_history(cls, account):
        changes_list = cls.query.filter(cls.item_id == account.id).order_by(
            cls.date.desc()
        )
        return [change.message_by_account for change in changes_list]
