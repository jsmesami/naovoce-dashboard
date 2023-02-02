from flask import render_template
from flask_login import login_required
from jinja2_fragments.flask import render_block

from ..extensions import htmx
from . import core, data
from . import parameters as par


@core.route("/charts")
@login_required
def charts():
    params = {
        "monthly_gains_chart": data.monthly_gains_chart(),
        "monthly_pois_chart": data.monthly_pois_chart(),
    }

    return render_template("charts.html", **params)


@core.route("/")
@login_required
def index():
    section = par.getset_param("section", par.DEFAULT_SECTION, par.guard_section)

    params = {
        "section": section,
    }

    if par.get_param(f"{section}_reset_filters", False, par.guard_bool):
        par.reset_filters(section)

    offset = par.getset_param(f"{section}_offset", 0, par.guard_offset)
    limit = par.getset_param(f"{section}_limit", par.DEFAULT_LIMIT, par.guard_limit)
    order = par.getset_param(
        f"{section}_order", par.DEFAULT_ORDER, par.guard_order(section)
    )
    show_controls = par.getset_param("show_controls", False, par.guard_bool)
    created_since = par.getset_param(
        f"{section}_created_since", par.MIN_CREATED(), par.guard_date
    )
    created_until = par.getset_param(
        f"{section}_created_until", par.MAX_CREATED(), par.guard_date
    )

    params |= {
        "offset": offset,
        "limit": limit,
        "order": order,
        "show_controls": show_controls,
        "created_since": created_since,
        "created_until": created_until,
        "created_min": par.MIN_CREATED(),
        "created_max": par.MAX_CREATED(),
    }

    if section == "pois":
        id_filter = par.get_param(f"pois_id_filter", 0, par.guard_posint)
        choices = data.cat_choices()
        cat_ids = (ch["id"] for ch in choices)
        cat_id_filter = par.getset_param(
            f"pois_cat_id_filter", 0, par.guard_category(cat_ids)
        )
        params |= {
            "id_filter": id_filter,
            "cat_choices": choices,
            "cat_id_filter": cat_id_filter,
        }

    if section == "creators":
        search = par.getset_param(f"creators_search", "", par.identity)
        id_filter = par.get_param(f"creators_id_filter", 0, par.guard_posint)
        visited_since = par.getset_param(
            f"creators_visited_since", par.MIN_VISITED(), par.guard_date
        )
        visited_until = par.getset_param(
            f"creators_visited_until", par.MAX_VISITED(), par.guard_date
        )
        params |= {
            "search": search,
            "id_filter": id_filter,
            "visited_since": visited_since,
            "visited_until": visited_until,
            "visited_min": par.MIN_VISITED(),
            "visited_max": par.MAX_VISITED(),
        }

    params |= par.SECTION_FETCHERS[section](**params)

    if htmx:
        return render_block("index.html", "content", **params)

    return render_template("index.html", **params)
