import calendar

from ..database import db
from datetime import datetime, date
from app.utils import ModelMixin
from sqlalchemy.orm import relationship
from sqlalchemy import desc, and_
from app.models.account_extensions import AccountExtension


class Account(db.Model, ModelMixin):
    """Account entity"""

    __tablename__ = "accounts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    phone_id = db.Column(db.Integer, db.ForeignKey("phones.id"), default=1)
    reseller_id = db.Column(db.Integer, db.ForeignKey("resellers.id"))
    sim = db.Column(db.String(20))
    imei = db.Column(db.String(60))
    comment = db.Column(db.String(256))
    activation_date = db.Column(db.DateTime, default=datetime.now)
    months = db.Column(db.Integer)
    deleted = db.Column(db.Boolean, default=False)
    product = relationship("Product")
    phone = relationship("Phone")
    reseller = relationship("Reseller")
    extensions = relationship("AccountExtension", viewonly=True)

    @staticmethod
    def __add_months(sourcedate: datetime, months: int) -> datetime:
        month = sourcedate.month - 1 + months
        year = sourcedate.year + month // 12
        month = month % 12 + 1
        day = min(sourcedate.day, calendar.monthrange(year, month)[1])
        return date(year, month, day)

    @property
    def expiration_date(self):
        enddate = (
            AccountExtension.query.with_entities(AccountExtension.end_date)
            .filter(self.id == AccountExtension.account_id)
            .order_by(desc(AccountExtension.end_date))
            .first()
        )
        if enddate:
            return enddate.end_date
        else:
            return self.__add_months(self.activation_date, self.months)

    # we fail here --> line 68 -->  change.value_str for change in self.changes.filter_by(change_type="name").all()
    # we delete account changes and no ref to history changes as i see...
    def to_dict(self) -> dict:
        from .history_changes import HistoryChange

        changes = HistoryChange.query.filter(
            and_(
                HistoryChange.change_type == HistoryChange.EditType.changes_account,
                HistoryChange.item_id == self.id,
            )
        )
        return {
            "id": self.id,
            "name": self.name,
            "product": self.product.name if self.product else "-=NONE=-",
            "phone": self.phone.name if self.phone else "",
            "imei": self.imei if self.imei else "",
            "reseller": self.reseller.name if self.reseller else "-=NONE=-",
            "sim": self.sim,
            "expiration_date": self.expiration_date.strftime("%Y-%m-%d"),
            "activation_date": self.activation_date.strftime("%Y-%m-%d"),
            "months": self.months,
            "prev_names": ", ".join(
                [
                    change.before_value_str
                    for change in changes.filter(
                        HistoryChange.value_name == "name"
                    ).all()
                ]
            ),
            "prev_sims": ", ".join(
                [
                    change.before_value_str
                    for change in changes.filter(
                        HistoryChange.value_name == "sim"
                    ).all()
                ]
            ),
        }

    @staticmethod
    def columns():
        return [
            "ID",
            "Name",
            "Product",
            "Phone",
            "IMEI",
            "Re-seller",
            "SIM",
            "Expiration Date",
            "Activation Date",
            "Months",
            "Prev. names",
            "Prev. SIMs",
        ]
