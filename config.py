import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PATH_TO_DOT_ENV_FILE = os.path.join(BASE_DIR, ".env")
load_dotenv(PATH_TO_DOT_ENV_FILE)


class BaseConfig(object):
    """Base configuration."""

    APP_NAME = os.environ.get("APP_NAME", "NITRIX")
    ACCOUNTS_PER_PAGE = 50
    DEBUG_TB_ENABLED = False
    SECRET_KEY = os.environ.get(
        "SECRET_KEY", "Ensure you set a secret key, this is important!"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    CSS_FOLDER = "css"
    JAVASCRIPT_FOLDER = "js"
    IMAGES_FOLDER = "images"
    DISABLE_OTP = bool(int(os.environ.get("DISABLE_OTP", "0")))
    ADMIN_NAME = os.environ.get("ADMIN_NAME", "admin")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "1234")
    REDIS_URL_FOR_CELERY = os.environ.get("REDIS_URL_FOR_CELERY", "redis://redis")
    CELERY_PERIODIC_CHECK_TIME = float(
        os.environ.get("CELERY_PERIODIC_CHECK_TIME", "10.0")
    )
    DATABASE_URL = os.environ.get("DATABASE_URL", "")
    DB_DUMP_DAYS_PERIOD = int(os.environ.get("DB_DUMP_DAYS_PERIOD", "30"))

    @staticmethod
    def configure(app):
        # Implement this method to do further configuration on your app.
        pass


class DevelopmentConfig(BaseConfig):
    """Development configuration."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DEVELOP_DATABASE_URL",
        "sqlite:///" + os.path.join(BASE_DIR, "database-develop.sqlite3"),
    )


class TestingConfig(BaseConfig):
    """Testing configuration."""

    TESTING = True
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "TEST_DATABASE_URL",
        "sqlite:///" + os.path.join(BASE_DIR, "database-test.sqlite3"),
    )


class ProductionConfig(BaseConfig):
    """Production configuration."""

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "database.sqlite3")
    )
    WTF_CSRF_ENABLED = True


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}

SIM_COST_DISCOUNT = float(os.environ.get("SIM_COST_DISCOUNT", 10)) * (-1.0)
SIM_COST_ACCOUNT_COMMENT = os.environ.get(
    "SIM_COST_ACCOUNT_COMMENT", "IMPORTANT! Sim cost discounted."
)
