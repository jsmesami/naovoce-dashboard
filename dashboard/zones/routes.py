from flask import render_template
from flask_login import login_required
from jinja2_fragments.flask import render_block

from . import zones


@zones.route("/zones")
@login_required
def index():
    params = {}

    return render_template("zones.html", **params)


@zones.route("/zones/<id>")
@login_required
def view():
    params = {"zone": {"mode": "edit"}}

    return render_block("zones.html", "zone_map", **params)


@zones.route("/zones/add")
@login_required
def add():
    params = {"zone": {"mode": "add"}}

    return render_block("zones.html", "zone_map", **params)
