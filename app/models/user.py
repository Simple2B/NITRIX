import enum
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from .. import db
from ..utils import ModelMixin
from sqlalchemy import Enum


class User(db.Model, UserMixin, ModelMixin):
    """User entity"""

    __tablename__ = 'users'

    class Type(enum.Enum):
        super_admin = 'super'
        admin = 'admin'
        user = 'user'

    class Status(enum.Enum):
        active = 'Active'
        not_active = 'Not active'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True, nullable=False)
    user_type = db.Column(Enum(Type), default=Type.user)
    password_hash = db.Column(db.String(255))
    password_val = db.Column(db.String(255))
    activated = db.Column(Enum(Status), default=Status.active)

    @hybrid_property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        self.password_val = password

    @classmethod
    def authenticate(cls, user_name, password):
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
