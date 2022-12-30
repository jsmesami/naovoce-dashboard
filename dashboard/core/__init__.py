from flask import Blueprint

core = Blueprint("core", __name__, cli_group="core")

from . import commands, routes
