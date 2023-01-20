from flask import abort, render_template, session
from flask_login import current_user

from ..extensions import db, htmx
from . import core, data
from . import parameters as par


def monthly_chart():
    query = """
        SELECT
        DATE_TRUNC('month', created) AS created_in_month,
        COUNT(id) AS count
        FROM {table}
        WHERE created >= '2015-01-01'
        GROUP BY DATE_TRUNC('month', created)
        ORDER BY created_in_month
    """
    creators = db.session.execute(query.format(table="creator")).all()
    pois = db.session.execute(query.format(table="poi")).all()

    return {
        "x_axis": ", ".join(dat.strftime("'%-m/%-y'") for dat, _cnt in creators),
        "creators": ", ".join(str(cnt) for _dat, cnt in creators),
        "pois": ", ".join(str(cnt) for _dat, cnt in pois),
    }


@core.route("/toggle-charts")
def toggle_charts():
    if not htmx:
        abort(403)

    show_charts = not session.get("show_charts")
    session["show_charts"] = show_charts
    params = {
        "show_charts": show_charts,
    }
    if show_charts:
        params |= {"monthly_chart": monthly_chart()}

    return render_template("inc/charts.html", **params)


@core.route("/")
def index():
    section = par.getset_param("section", par.DEFAULT_SECTION, par.guard_section)

    params = {
        "section": section,
    }

    if current_user.is_authenticated:
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
        session["show_charts"] = False

        params |= {
            "show_charts": session["show_charts"],
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
            return render_template("inc/stats.html", **params)

    return render_template("index.html", **params)
