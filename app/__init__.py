"""Flask-app factory"""
import os

from flask import Flask, render_template
from flask_login import LoginManager
from werkzeug.exceptions import HTTPException
from .database import db

# instantiate extensions
login_manager = LoginManager()


def create_app(environment="development"):

    from config import config
    from .views import main_blueprint, auth_blueprint, account_blueprint
    from .views import product_blueprint, reseller_blueprint, user_blueprint
    from .models import User
    from .logger import log

    # Instantiate app.
    app = Flask(__name__)
    log.set_level(log.DEBUG)
    log(log.INFO, 'start server')
    # Set app config.
    env = os.environ.get("FLASK_ENV", environment)
    app.config.from_object(config[env])
    config[env].configure(app)

    # Set up extensions.
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints.
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(account_blueprint)
    app.register_blueprint(product_blueprint)
    app.register_blueprint(reseller_blueprint)
    app.register_blueprint(user_blueprint)

    # Set up flask login.
    @login_manager.user_loader
    def get_user(id):
        return User.query.get(int(id))

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    # Error handlers.
    @app.errorhandler(HTTPException)
    def handle_http_error(exc):
        return render_template("error.html", error=exc), exc.code

    return app
