import os
import re

from flask import render_template, request, session
from flask_login import current_user
from sqlalchemy import select

from ..extensions import db, htmx
from . import core
from .models import POI, Category, Comment, Creator, Image


def creators(limit, offset, **args):
    statement = (
        select(
            Creator.id,
            Creator.first_name,
            Creator.last_name,
            Creator.email,
            Creator.created,
            Creator.last_visit,
        )
        .limit(limit)
        .offset(offset)
    )
    return {"rows": db.session.execute(statement).mappings().all()}


def categories(limit, offset, **args):
    statement = (
        select(
            Category.id,
            Category.created,
            Category.name,
        )
        .limit(limit)
        .offset(offset)
    )
    return {"rows": db.session.execute(statement).mappings().all()}


def pois(limit, offset, **args):
    statement = (
        select(
            POI.id,
            POI.created,
            POI.display_count,
            POI.position,
        )
        .limit(limit)
        .offset(offset)
    )
    return {"rows": db.session.execute(statement).mappings().all()}


def images(limit, offset, **args):
    statement = (
        select(
            Image.id,
            Image.created,
            Image.image_url,
        )
        .limit(limit)
        .offset(offset)
    )
    return {
        "rows": (
            dict(i) | {"file_name": os.path.basename(i.get("image_url", ""))}
            for i in db.session.execute(statement).mappings().all()
        )
    }


def comments(limit, offset, **args):
    statement = (
        select(
            Comment.id,
            Comment.created,
            Comment.text,
        )
        .limit(limit)
        .offset(offset)
    )
    return {"rows": db.session.execute(statement).mappings().all()}


DEFAULT_LIMIT = 100
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
