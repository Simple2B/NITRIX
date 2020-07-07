from app import db
from flask_app import create_database


def create_mock_db():
    """create test DB
    """
    db.drop_all()
    create_database()
