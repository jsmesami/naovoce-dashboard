from flask import Blueprint

core = Blueprint("core", __name__, cli_group="core")


@core.app_template_filter()
def format_coord(coord):
    return "{:.10f}".format(coord).rjust(14, "\u2000")


# Import last to avoid circular dependency
from . import commands, routes
