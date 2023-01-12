from flask import render_template
from flask_login import current_user

from ..extensions import htmx
from . import core
from . import request_params as rp
from .data_fetchers import cat_choices


@core.route("/")
def index():
    section = rp.getset_param("section", rp.DEFAULT_SECTION, rp.guard_section)

    params = {
        "section": section,
    }

    if current_user.is_authenticated:
        if rp.get_param(f"{section}_reset_filters", False, rp.guard_bool):
            rp.reset_filters(section)

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

        if section == "pois":
            choices = cat_choices()
            cat_ids = (ch["id"] for ch in choices)
            cat_id_filter = rp.getset_param(
                f"{section}_cat_id_filter", 0, rp.guard_category(cat_ids)
            )
            params |= {
                "cat_choices": choices,
                "cat_id_filter": cat_id_filter,
            }

        if section in ("creators", "pois"):
            params |= {
                "id_filter": rp.get_param(f"{section}_id_filter", 0, rp.guard_posint)
            }

        params |= rp.SECTION_FETCHERS[section](**params)

        if htmx:
            return render_template("inc/stats.html", **params)

    return render_template("index.html", **params)
