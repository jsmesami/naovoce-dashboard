from flask import abort, render_template, session
from flask_login import login_required
from jinja2_fragments.flask import render_block

from ..extensions import htmx
from . import core
from . import parameters as par


@core.route("/download_csv/<section>")
@login_required
def download_csv(section):
    section = par.guard_section(section, None)
    if section is None:
        abort(400)

    params = par.section_params(section, paginate=False)
    csv_rows = par.SECTION_ROWS_FETCHERS[section](**params)

    return render_template(f"tables/{section}-csv.txt", **csv_rows)


@core.route("/toggle_controls")
@login_required
def toggle_controls():
    if not htmx:
        abort(403)

    section = par.getset_param("section", par.DEFAULT_SECTION, par.guard_section)
    show_controls = not session.get("show_controls", False)
    session["show_controls"] = show_controls

    params = {"show_controls": show_controls}
    params |= par.section_params(section)
    params |= par.SECTION_COUNT_FETCHERS[section](**params)

    return render_block("tables/base.html", "table_controls", **params)


@core.route("/")
@login_required
def index():
    section = par.getset_param("section", par.DEFAULT_SECTION, par.guard_section)
    show_controls = par.getset_param("show_controls", False, par.guard_bool)

    params = {"show_controls": show_controls}
    params |= par.section_params(section)
    params |= par.SECTION_ROWS_FETCHERS[section](**params)
    params |= par.SECTION_COUNT_FETCHERS[section](**params)

    if htmx:
        return render_block("index.html", "content", **params)

    return render_template("index.html", **params)
