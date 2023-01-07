import os
import re

from flask import render_template, request, session
from flask_login import current_user

from ..extensions import db, htmx
from . import core


def creators(**args):
    statement = """
        SELECT
        c.id, c.created, c.first_name, c.last_name, c.email, c.last_visit,
        (SELECT COUNT(*) FROM poi WHERE poi.creator_id = c.id) AS n_pois,
        (SELECT COUNT(*) FROM image WHERE image.creator_id = c.id) AS n_images,
        (SELECT COUNT(*) FROM comment WHERE comment.creator_id = c.id) AS n_comments
        FROM creator c
        LIMIT :limit OFFSET :offset;
    """
    return {"rows": db.session.execute(statement, args).mappings().all()}


def categories(**args):
    statement = """
        SELECT
        cat.id, cat.created, cat.name,
        (SELECT COUNT(*) FROM poi WHERE poi.category_id = cat.id) AS n_pois
        FROM category cat
        LIMIT :limit OFFSET :offset;
    """
    return {"rows": db.session.execute(statement, args).mappings().all()}


def pois(**args):
    statement = """
        SELECT
        poi.id, poi.created, poi.display_count,
        ST_X(poi.position) AS lng,
        ST_Y(poi.position) AS lat,
        poi.creator_id, poi.category_id,
        cat.name AS category,
        (SELECT COUNT(*) FROM image WHERE image.poi_id = poi.id) AS n_images,
        (SELECT COUNT(*) FROM comment WHERE comment.poi_id = poi.id) AS n_comments
        FROM poi
        LEFT JOIN category cat ON cat.id = poi.category_id
        LIMIT :limit OFFSET :offset;
    """
    return {"rows": db.session.execute(statement, args).mappings().all()}


def images(**args):
    statement = """
        SELECT
        id, created, image_url, creator_id, poi_id
        FROM image LIMIT :limit OFFSET :offset;
    """
    return {
        "rows": (
            dict(i) | {"file_name": os.path.basename(i.get("image_url", ""))}
            for i in db.session.execute(statement, args).mappings().all()
        )
    }


def comments(**args):
    statement = """
        SELECT
        id, created, "text", creator_id, poi_id
        FROM comment;
    """
    return {"rows": db.session.execute(statement, args).mappings().all()}


DEFAULT_LIMIT = 40
DEFAULT_SECTION = "creators"
SECTIONS = ("creators", "categories", "pois", "images", "comments")
FETCHERS = (creators, categories, pois, images, comments)
SECTION_FETCHERS = dict(zip(SECTIONS, FETCHERS))


def getset_param(key, default, adapt=None):
    if (ret := request.args.get(key)) is None:
        ret = session.get(key, default)
    if adapt is not None:
        try:
            ret = adapt(ret)
        except (ValueError, TypeError):
            ret = default

    session[key] = ret
    return ret


def guard_section(section):
    if match := re.match(rf"({'|'.join(SECTIONS)})", section):
        return match.group(0)

    return DEFAULT_SECTION


@core.route("/")
def index():
    section = getset_param("section", "creators", guard_section)
    params = {
        "section": section,
    }
    if current_user.is_authenticated:
        offset = getset_param(f"{section}_offset", 0, int)
        limit = getset_param(f"{section}_limit", DEFAULT_LIMIT, int)

        params |= {
            "offset": offset,
            "limit": limit,
        }

        params |= SECTION_FETCHERS[section](**params)

        if htmx:
            return render_template("inc/stats.html", **params)

    return render_template("index.html", **params)
