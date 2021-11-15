import base64
import os
import enum
import onetimepass
from flask import current_app
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy import Enum
from .. import db
from ..utils import ModelMixin


def gen_secret_key():
    return base64.b32encode(os.urandom(20)).decode("utf-8")


class User(db.Model, UserMixin, ModelMixin):
    """User entity"""

    __tablename__ = "users"

    @staticmethod
    def gen_secret():
        return gen_secret_key()

    class Type(enum.Enum):
        super_admin = "super_admin"
        admin = "admin"
        user = "user"

    class Status(enum.Enum):
        active = "Active"
        not_active = "Not active"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True, nullable=False)
    user_type = db.Column(Enum(Type), default=Type.user)
    password_hash = db.Column(db.String(255))
    activated = db.Column(Enum(Status), default=Status.active)
    deleted = db.Column(db.Boolean, default=False)
    otp_secret = db.Column(db.String(32), default=gen_secret_key)
    otp_active = db.Column(db.Boolean, default=False)

    @hybrid_property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def get_totp_uri(self):
        """generate authentication URI for Google Authenticator"""
        return "otpauth://totp/{0}:{1}?secret={2}&issuer={0}".format(
            current_app.config["APP_NAME"], self.name, self.otp_secret
        )

    def verify_totp(self, token):
        """validates 6-digit OTP code retrieved from Google"""
        int_token = int(token)
        return onetimepass.valid_totp(f"{int_token:06d}", self.otp_secret)

    @classmethod
    def authenticate(cls, user_name, password):
        user = cls.query.filter(cls.name == user_name).first()
        if user is not None and check_password_hash(user.password, password):
            return user

    def __repr__(self):
        return f"<{self.id} {self.name}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "type": (self.user_type.name if self.user_type else "None"),
            "status": self.activated.name,
        }

    @staticmethod
    def columns():
        return ["ID", "Name", "Type", "Status"]
