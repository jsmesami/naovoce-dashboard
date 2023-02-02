from flask import abort, render_template, session
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


@core.route("/toggle_controls")
def toggle_controls():
    if not htmx:
        abort(403)

    section = par.getset_param("section", par.DEFAULT_SECTION, par.guard_section)
    show_controls = not session.get("show_controls", False)
    session["show_controls"] = show_controls

    params = par.section_params(section, show_controls)
    params |= par.SECTION_COUNT_FETCHERS[section](**params)

    return render_block("tables/base.html", "table_controls", **params)


@core.route("/")
@login_required
def index():
    section = par.getset_param("section", par.DEFAULT_SECTION, par.guard_section)
    show_controls = par.getset_param("show_controls", False, par.guard_bool)

    params = par.section_params(section, show_controls)
    params |= par.SECTION_ROWS_FETCHERS[section](**params)
    params |= par.SECTION_COUNT_FETCHERS[section](**params)

    if htmx:
        return render_block("index.html", "content", **params)

    return render_template("index.html", **params)
