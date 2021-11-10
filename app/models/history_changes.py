import enum
from ..database import db
from sqlalchemy import Enum
from datetime import datetime
from sqlalchemy.orm import relationship
from app.utils import ModelMixin


def get_current_user_id():
    from flask_login import current_user

    return current_user.id


class HistoryChange(db.Model, ModelMixin):
    """Model for extension account info"""

    __tablename__ = "history_changes"

    class EditType(enum.Enum):
        creation_account = "creation_account"
        # extension_account = "extension_account"
        deletion_account = "deletion_account"
        changes_account = "changes_account"
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
    user = relationship("User", backref=db.backref("changes", lazy="dynamic"))

    @property
    def message_by_account(self):
        if self.change_type == self.EditType.creation_account:
            return f"[{self.date.strftime('%Y/%m/%d, %H:%M')}] Created by user [{self.user.name}]"
        elif self.change_type == self.EditType.deletion_account:
            return f"[{self.date.strftime('%Y/%m/%d, %H:%M')}] Deleted by user [{self.user.name}]"
        return "[{}] User [{}] changed [{}] value from [{}] to [{}]".format(
            self.date.strftime("%Y/%m/%d, %H:%M:%S"),
            self.user.name,
            self.value_name,
            self.before_value_str,
            self.after_value_str,
        )

    # @property
    # def message_by_user(self):
    #     if self.change_type == self.ChangeType.created:
    #         return f"[{self.date.strftime('%Y/%m/%d, %H:%M')}] Created account [{self.account.name}]"
    #     elif self.change_type == self.ChangeType.deleted:
    #         return f"[{self.date.strftime('%Y/%m/%d, %H:%M')}] Deleted account [{self.account.name}]"
    #     return "[{}] Changed [{}] value from [{}] to [{}] in account [{}]".format(
    #         self.date.strftime("%Y/%m/%d, %H:%M:%S"),
    #         self.change_type.value,
    #         self.value_str,
    #         self.new_value_str,
    #         self.account.name,
    #     )

    @classmethod
    def get_history(cls, account):
        changes_list = cls.query.filter(cls.item_id == account.id).order_by(
            cls.date.desc()
        )
        return [change.message_by_account for change in changes_list]
