from flask import abort, json, render_template, request
from flask_login import current_user, login_required
from jinja2_fragments.flask import render_block
from shapely.geometry import MultiPolygon, shape
from sqlalchemy import text

from ..extensions import db, htmx
from ..zones.models import Zone
from . import data, zones


def get_zones():
    return db.session.execute(text(data.ZONES_SELECT)).mappings().all()


def get_zone(id):
    return (
        db.session.execute(text(data.ZONE_GET), {"zone_id": id}).mappings().fetchone()
    )


def to_shapes(geojson):
    """Make Shapely shapes, converting MultiPolygon to sequence of Polygons"""
    for feat in geojson.get("features", []):
        geom = feat.get("geometry", {})
        match geom.get("type"):
            case "MultiPolygon":
                yield from (
                    shape({"type": "Polygon", "coordinates": coords})
                    for coords in geom.get("coordinates")
                )
            case "Polygon":
                yield shape(geom)
            case _:
                yield shape({"type": "Polygon", "coordinates": []})


@zones.route("/zones", methods=["GET", "POST"])
@login_required
def index():
    if not htmx:
        return render_template("zones.html", rows=get_zones())

    if request.method == "POST":
        area = MultiPolygon(to_shapes(json.loads(request.form["zone_area"])))
        db.session.add(
            Zone(name=request.form["zone_name"], author=current_user, area=str(area))
        )
        db.session.commit()
        return render_block("zones.html", "content", rows=get_zones())

    return render_block("zones.html", "zone_map", zone={"mode": "add"})


@zones.route("/zones/<id>", methods=["GET", "POST", "DELETE"])
@login_required
def detail(id):
    if not htmx:
        abort(403)

    zone = get_zone(id)

    if request.method == "POST":
        area = MultiPolygon(to_shapes(json.loads(request.form["zone_area"])))
        db.session.execute(
            text(data.ZONE_UPDATE),
            {
                "zone_id": id,
                "name": request.form["zone_name"],
                "author": current_user.id,
                "area": str(area),
            },
        )
        db.session.commit()
        return render_block("zones.html", "content", rows=get_zones())

    if request.method == "DELETE":
        db.session.execute(text(data.ZONE_DELETE), {"zone_id": zone.id})
        db.session.commit()
        return render_block("zones.html", "content", rows=get_zones())

    return render_block("zones.html", "zone_map", zone=dict(zone) | {"mode": "edit"})
