from flask import render_template
from flask_login import login_required

from . import charts, data


@charts.route("/charts")
@login_required
def index():
    params = {
        "monthly_gains_chart": data.monthly_gains_chart(),
        "monthly_pois_chart": data.monthly_pois_chart(),
        "cz_geojson": data.cz_geojson(),
        "cz_area_counts": data.cz_area_counts(),
    }

    return render_template("charts.html", **params)
