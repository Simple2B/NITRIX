import enum
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from .. import db
from ..utils import ModelMixin
from sqlalchemy import Enum
import base64
import os
import onetimepass


class User(db.Model, UserMixin, ModelMixin):
    """User entity"""

    __tablename__ = 'users'

    class Type(enum.Enum):
        super_admin = 'super_admin'
        admin = 'admin'
        user = 'user'

    class Status(enum.Enum):
        active = 'Active'
        not_active = 'Not active'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True, nullable=False)
    user_type = db.Column(Enum(Type), default=Type.user)
    password_hash = db.Column(db.String(255))
    activated = db.Column(Enum(Status), default=Status.active)
    deleted = db.Column(db.Boolean, default=False)
    otp_secret = db.Column(db.String(16))
    otp_active = db.Column(db.Boolean, default=False)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.otp_secret is None:
            # generate a random otp secret (16 chars)
            self.otp_secret = base64.b32encode(os.urandom(10)).decode('utf-8')

    @hybrid_property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def get_totp_uri(self):
        ''' generate authentication URI for Google Authenticator '''
        return f'otpauth://totp/NITRIX:{self.name}?secret={self.otp_secret}&issuer=NITRIX'

    def verify_totp(self, token):
        ''' validates 6-digit OTP code retrieved from Google '''
        return onetimepass.valid_totp(token, self.otp_secret)

    @classmethod
    def authenticate(cls, user_name, password, token):
        user = cls.query.filter(cls.name == user_name).first()
        if user is not None and check_password_hash(user.password, password):
            return user

    def __str__(self):
        return f'<User: {self.name}>'

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'type': (self.user_type.name if self.user_type else 'None'),
            'status': self.activated.name
        }

    @staticmethod
    def columns():
        return ['ID', 'Name', 'Type', 'Status']
