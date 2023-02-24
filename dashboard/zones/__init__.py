from flask import Blueprint

zones = Blueprint("zones", __name__, cli_group="zones")

# Import last to avoid circular dependency
from . import routes
