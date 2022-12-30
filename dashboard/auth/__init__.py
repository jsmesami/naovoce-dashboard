from flask import Blueprint

auth = Blueprint("auth", __name__, cli_group="auth")

from . import commands, routes
