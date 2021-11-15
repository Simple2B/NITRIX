import enum
from ..database import db
from sqlalchemy import Enum
from datetime import datetime
from app.utils import ModelMixin
from sqlalchemy.orm import relationship


class Reseller(db.Model, ModelMixin):
    """Reseller entity"""

    __tablename__ = "resellers"

    class Status(enum.Enum):
        active = "Active"
        not_active = "Not active"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True, nullable=False)
    status = db.Column(Enum(Status), default=Status.active)
    comments = db.Column(db.String(60))
    deleted = db.Column(db.Boolean, default=False)
    last_activity = db.Column(db.DateTime, default=datetime.now)
    ninja_client_id = db.Column(db.String(64))
    products = relationship("ResellerProduct")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "last_activity": self.last_activity.strftime("%Y-%m-%d-%H-%M"),
            "status": self.status.value,
        }

    @staticmethod
    def columns():
        return ["ID", "Name", "last Activity", "Status"]
