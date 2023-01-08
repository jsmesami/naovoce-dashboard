import os
import re

from flask import render_template, request, session
from flask_login import current_user

from ..extensions import db, htmx
from . import core


def creators(**args):
    query = """
        SELECT
        c.id, c.created, c.first_name, c.last_name, c.email, c.last_visit,
        (SELECT COUNT(*)
         FROM poi
         WHERE poi.creator_id = c.id
         AND poi.is_published = true) AS n_pois,
        (SELECT COUNT(*)
         FROM image
         WHERE image.creator_id = c.id
         AND image.is_published = true) AS n_images,
        (SELECT COUNT(*)
         FROM comment
         WHERE comment.creator_id = c.id
         AND comment.is_published = true) AS n_comments
        FROM creator c
        ORDER BY c.created DESC
        LIMIT :limit OFFSET :offset;
    """
    count = """
        SELECT COUNT(*)
        FROM creator
    """
    return {"rows": db.session.execute(query, args).mappings().all()} | dict(
        db.session.execute(count).mappings().fetchone()
    )


def categories(**args):
    query = """
        SELECT
        cat.id, cat.created, cat.name,
        (SELECT COUNT(*)
         FROM poi
         WHERE poi.category_id = cat.id
         AND poi.is_published = true) AS n_pois
        FROM category cat
        WHERE cat.is_published = true
        ORDER BY cat.created DESC
        LIMIT :limit OFFSET :offset;
    """
    count = """
        SELECT COUNT(*)
        FROM category
        WHERE is_published = true
    """
    return {"rows": db.session.execute(query, args).mappings().all()} | dict(
        db.session.execute(count).mappings().fetchone()
    )


def pois(**args):
    query = """
        SELECT
        poi.id, poi.created, poi.display_count, poi.creator_id, poi.category_id,
        cat.name AS category,
        ST_X(poi.position) AS lng,
        ST_Y(poi.position) AS lat,
        (SELECT COUNT(*)
         FROM image
         WHERE image.poi_id = poi.id
         AND image.is_published = true) AS n_images,
        (SELECT COUNT(*)
         FROM comment
         WHERE comment.poi_id = poi.id
         AND comment.is_published = true) AS n_comments
        FROM poi
        LEFT JOIN category cat ON cat.id = poi.category_id
        WHERE poi.is_published = true
        ORDER BY poi.created DESC
        LIMIT :limit OFFSET :offset;
    """
    count = """
        SELECT COUNT(*)
        FROM poi
        WHERE is_published = true
    """
    return {"rows": db.session.execute(query, args).mappings().all()} | dict(
        db.session.execute(count).mappings().fetchone()
    )


def images(**args):
    query = """
        SELECT
        id, created, image_url, creator_id, poi_id
        FROM image
        WHERE is_published = true
        ORDER BY created DESC
        LIMIT :limit OFFSET :offset;
    """
    count = """
        SELECT COUNT(*)
        FROM image
        WHERE is_published = true
    """
    return {
        "rows": (
            dict(i) | {"file_name": os.path.basename(i.get("image_url", ""))}
            for i in db.session.execute(query, args).mappings().all()
        )
    } | dict(db.session.execute(count).mappings().fetchone())


def comments(**args):
    query = """
        SELECT
        id, created, "text", creator_id, poi_id
        FROM comment
        WHERE is_published = true
        ORDER BY created DESC
        LIMIT :limit OFFSET :offset;
    """
    count = """
        SELECT COUNT(*)
        FROM comment
        WHERE is_published = true
    """
    return {"rows": db.session.execute(query, args).mappings().all()} | dict(
        db.session.execute(count).mappings().fetchone()
    )


DEFAULT_LIMIT = 40
DEFAULT_SECTION = "creators"
SECTIONS = ("creators", "categories", "pois", "images", "comments")
FETCHERS = (creators, categories, pois, images, comments)
SECTION_FETCHERS = dict(zip(SECTIONS, FETCHERS))


def getset_param(key, default, adapter):
    if (ret := request.args.get(key)) is None:
        ret = session.get(key, default)

    try:
        ret = adapter(ret, default)
    except (ValueError, TypeError):
        ret = default

    session[key] = ret
    return ret


def guard_section(section, default):
    if match := re.match(rf"({'|'.join(SECTIONS)})", section):
        return match.group(0)

    return default


def guard_zero_positive(n, default):
    try:
        ret = int(n)
        return ret if ret >= 0 else default
    except (ValueError, TypeError):
        return default


@core.route("/")
def index():
    section = getset_param("section", DEFAULT_SECTION, guard_section)
    params = {
        "section": section,
    }
    if current_user.is_authenticated:
        offset = getset_param(f"{section}_offset", 0, guard_zero_positive)
        limit = getset_param(f"{section}_limit", DEFAULT_LIMIT, guard_zero_positive)

        params |= {
            "offset": offset,
            "limit": limit,
        }

        params |= SECTION_FETCHERS[section](**params)

        if htmx:
            return render_template("inc/stats.html", **params)

    return render_template("index.html", **params)
