from flask import render_template
from flask_login import current_user

from ..extensions import htmx
from . import core
from . import request_params as rp


@core.route("/")
def index():
    section = rp.getset_param("section", rp.DEFAULT_SECTION, rp.guard_section)

    params = {
        "section": section,
    }

    if current_user.is_authenticated:
        offset = rp.getset_param(f"{section}_offset", 0, rp.guard_offset)
        limit = rp.getset_param(f"{section}_limit", rp.DEFAULT_LIMIT, rp.guard_limit)
        order = rp.getset_param(
            f"{section}_order", rp.DEFAULT_ORDER, rp.guard_order(section)
        )
        show_controls = rp.getset_param("show_controls", False, rp.guard_bool)
        created_since = rp.getset_param(
            f"{section}_created_since", rp.MIN_CREATED, rp.guard_date
        )
        created_until = rp.getset_param(
            f"{section}_created_until", rp.MAX_CREATED, rp.guard_date
        )

        params |= {
            "offset": offset,
            "limit": limit,
            "order": order,
            "show_controls": show_controls,
            "created_since": created_since,
            "created_until": created_until,
            "created_min": rp.MIN_CREATED,
            "created_max": rp.MAX_CREATED,
        }

        params |= rp.SECTION_FETCHERS[section](**params)

        if htmx:
            return render_template("inc/stats.html", **params)

    return render_template("index.html", **params)
