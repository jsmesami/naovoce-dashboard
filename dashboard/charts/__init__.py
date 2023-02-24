from flask import Blueprint

charts = Blueprint("charts", __name__, cli_group="charts")

# Import last to avoid circular dependency
from . import routes
