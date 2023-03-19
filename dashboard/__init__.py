"""Statistics Dashboard for Na-ovoce.cz"""
from flask import Flask

from .auth.models import User
from .config import Config
from .core.models import *
from .core.parameters import next_order
from .extensions import db, htmx, login_manager
from .zones.models import Zone

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
    login_manager.login_view = "auth.login"

    from .api import api
    from .auth import auth
    from .charts import charts
    from .core import core
    from .zones import zones

    app.register_blueprint(api)
    app.register_blueprint(auth)
    app.register_blueprint(charts)
    app.register_blueprint(core)
    app.register_blueprint(zones)

    @app.context_processor
    def context():
        return dict(next_order=next_order)

    return app
