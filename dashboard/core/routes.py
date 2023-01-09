from flask import render_template
from flask_login import current_user

from ..extensions import htmx
from . import core
from .request_params import (
    DEFAULT_LIMIT,
    DEFAULT_ORDER,
    DEFAULT_SECTION,
    SECTION_FETCHERS,
    getset_param,
    guard_order,
    guard_section,
    guard_zero_positive,
)


@core.route("/")
def index():
    section = getset_param("section", DEFAULT_SECTION, guard_section)
    params = {
        "section": section,
    }
    if current_user.is_authenticated:
        offset = getset_param(f"{section}_offset", 0, guard_zero_positive)
        limit = getset_param(f"{section}_limit", DEFAULT_LIMIT, guard_zero_positive)
        order = getset_param(f"{section}_order", DEFAULT_ORDER, guard_order(section))

        params |= {
            "offset": offset,
            "limit": limit,
            "order": order,
        }

        params |= SECTION_FETCHERS[section](**params)

        if htmx:
            return render_template("inc/stats.html", **params)

    return render_template("index.html", **params)
