"""Statistics Dashboard for Na-ovoce.cz"""
from flask import Flask

from .auth.models import User
from .config import Config
from .core.models import *
from .core.parameters import next_order
from .extensions import db, htmx, login_manager

__version__ = "0.1.0"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def create_app(config_class=Config):
    app = Flask("dashboard")
    app.config.from_object(config_class)

    db.init_app(app)
    htmx.init_app(app)
    login_manager.init_app(app)

    from .auth import auth

    app.register_blueprint(auth)

    from .core import core

    app.register_blueprint(core)

    from .api import api

    app.register_blueprint(api)

    @app.context_processor
    def context():
        return dict(next_order=next_order)

    return app
