from flask_htmx import HTMX
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
htmx = HTMX()
login_manager = LoginManager()
