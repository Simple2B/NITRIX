"""Flask-app factory"""
import os
from datetime import timedelta

from flask import Flask, render_template, session
from flask_login import LoginManager
from werkzeug.exceptions import HTTPException
from .database import db, migrate

# instantiate extensions
login_manager = LoginManager()
login_manager.needs_refresh_message = u"Session timedout, please re-login"
login_manager.needs_refresh_message_category = "info"


def create_app(environment="development"):

    from config import config
    from .views import (
        main_blueprint,
        auth_blueprint,
        account_blueprint,
        reseller_product_blueprint,
    )
    from .views import (
        product_blueprint,
        reseller_blueprint,
        user_blueprint,
        phone_blueprint,
    )
    from .views import account_extension_blueprint
    from .models import User
    from .logger import log

    # Instantiate app.
    app = Flask(__name__)
    log.set_level(log.DEBUG)
    # Set app config.
    env = os.environ.get("FLASK_ENV", environment)
    app.config.from_object(config[env])
    config[env].configure(app)

    # Set up extensions.
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Register blueprints.
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(account_blueprint)
    app.register_blueprint(account_extension_blueprint)
    app.register_blueprint(product_blueprint)
    app.register_blueprint(phone_blueprint)
    app.register_blueprint(reseller_blueprint)
    app.register_blueprint(user_blueprint)
    app.register_blueprint(reseller_product_blueprint)

    # Set up flask login.
    @login_manager.user_loader
    def get_user(user_id: int):
        # return User.query.get(int(user_id))
        return User.query.filter(User.id == user_id).first()

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    # Error handlers.
    @app.errorhandler(HTTPException)
    def handle_http_error(exc):
        return render_template("error.html", error=exc), exc.code

    @app.before_request
    def before_request():
        session.permanent = True
        app.permanent_session_lifetime = timedelta(hours=2)

    return app
