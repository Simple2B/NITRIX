from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db
from sqlalchemy_utils.types.choice import ChoiceType


class User(db.Model):
    """User entity"""

    TYPES = (
        ("super_user", "Super user"),
        ("admin", "Admin"),
        ("user", "User"),
    )

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True, nullable=False)
    user_type = db.Column(ChoiceType(TYPES))
    password = db.Column(db.String(255), nullable=False)
    activated = db.Column(db.Boolean, default=False)

    @hybrid_property
    def password(self):
        return self.password

    @password.setter
    def password(self, password):
        self.password = generate_password_hash(password)

    @classmethod
    def authenticate(cls, user_id, password):
        user = cls.query.filter(cls.name == user_id).first()
        if user is not None and check_password_hash(user.password, password):
            return user

    def __str__(self):
        return f"<User: {self.name}>"
