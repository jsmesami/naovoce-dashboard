import os

from ..extensions import db


def order_clause(order):
    return "ORDER BY " + " ".join(order.rsplit("_", maxsplit=1))


def cat_id_filter_clause(cat_id_filter):
    return f"AND category_id = {cat_id_filter}" if cat_id_filter else ""


def id_filter_clause(id_filter, prefix=None):
    prefix = f"{prefix}." if prefix else ""
    return f"AND {prefix}id = {id_filter}" if id_filter else ""


def creator_search_clause(search):
    if not search:
        return ""

    return """
        AND (
        email LIKE :search
        OR first_name LIKE :search
        OR last_name LIKE :search)
    """


def creators(
    created_since,
    created_until,
    visited_since,
    visited_until,
    order,
    limit,
    offset,
    id_filter,
    search,
    **kwargs,
):
    query = f"""
        SELECT
        c.id, c.created, c.first_name, c.last_name, c.email, c.last_visit,
        to_char(c.created, 'DD.MM.YYYY') AS created_fmt,
        to_char(c.last_visit, 'DD.MM.YYYY') AS last_visit_fmt,
        (SELECT COUNT(*)
         FROM poi
         WHERE poi.creator_id = c.id
         AND poi.is_published = true
         AND poi.is_deleted = false) AS n_pois,
        (SELECT COUNT(*)
         FROM image
         WHERE image.creator_id = c.id
         AND image.is_published = true
         AND image.is_deleted = false) AS n_images,
        (SELECT COUNT(*)
         FROM comment
         WHERE comment.creator_id = c.id
         AND comment.is_published = true
         AND comment.is_deleted = false) AS n_comments
        FROM creator c
        WHERE c.is_deleted = false
        AND c.created BETWEEN '{created_since}' AND '{created_until}'
        AND c.last_visit BETWEEN '{visited_since}' AND '{visited_until}'
        {id_filter_clause(id_filter)}
        {creator_search_clause(search)}
        {order_clause(order)}
        LIMIT {limit} OFFSET {offset}
    """
    count = f"""
        SELECT COUNT(*)
        FROM creator
        WHERE is_deleted = false
        AND created BETWEEN '{created_since}' AND '{created_until}'
        {id_filter_clause(id_filter)}
        {creator_search_clause(search)}
    """
    return {
        "rows": db.session.execute(query, dict(search=f"%{search}%")).mappings().all()
    } | dict(
        db.session.execute(count, dict(search=f"%{search}%")).mappings().fetchone()
    )


def categories(created_since, created_until, order, limit, offset, **kwargs):
    query = f"""
        SELECT
        cat.id, cat.created, cat.name,
        to_char(cat.created, 'DD.MM.YYYY') AS created_fmt,
        (SELECT COUNT(*)
         FROM poi
         WHERE poi.category_id = cat.id
         AND poi.is_published = true
         AND poi.is_deleted = false) AS n_pois
        FROM category cat
        WHERE cat.is_published = true
        AND cat.is_deleted = false
        AND cat.created BETWEEN '{created_since}' AND '{created_until}'
        {order_clause(order)}
        LIMIT {limit} OFFSET {offset}
    """
    count = f"""
        SELECT COUNT(*)
        FROM category
        WHERE is_published = true
        AND is_deleted = false
        AND created BETWEEN '{created_since}' AND '{created_until}'
    """
    return {"rows": db.session.execute(query).mappings().all()} | dict(
        db.session.execute(count).mappings().fetchone()
    )


def pois(
    created_since,
    created_until,
    order,
    limit,
    offset,
    cat_id_filter,
    id_filter,
    **kwargs,
):
    query = f"""
        SELECT
        poi.id, poi.created, poi.display_count, poi.creator_id, poi.category_id,
        cat.name AS category_name,
        to_char(poi.created, 'DD.MM.YYYY') AS created_fmt,
        ST_X(poi.position) AS lng,
        ST_Y(poi.position) AS lat,
        (SELECT COUNT(*)
         FROM image
         WHERE image.poi_id = poi.id
         AND image.is_published = true
         AND image.is_deleted = false) AS n_images,
        (SELECT COUNT(*)
         FROM comment
         WHERE comment.poi_id = poi.id
         AND comment.is_published = true
         AND comment.is_deleted = false) AS n_comments
        FROM poi
        LEFT JOIN category cat ON cat.id = poi.category_id
        WHERE poi.is_published = true
        AND poi.is_deleted = false
        AND poi.created BETWEEN '{created_since}' AND '{created_until}'
        {cat_id_filter_clause(cat_id_filter)}
        {id_filter_clause(id_filter, 'poi')}
        {order_clause(order)}
        LIMIT {limit} OFFSET {offset}
    """
    count = f"""
        SELECT COUNT(*)
        FROM poi
        WHERE is_published = true
        AND is_deleted = false
        AND created BETWEEN '{created_since}' AND '{created_until}'
        {cat_id_filter_clause(cat_id_filter)}
        {id_filter_clause(id_filter, 'poi')}
    """
    return {"rows": db.session.execute(query).mappings().all()} | dict(
        db.session.execute(count).mappings().fetchone()
    )


def images(created_since, created_until, order, limit, offset, **kwargs):
    query = f"""
        SELECT
        id, created, image_url, creator_id, poi_id,
        to_char(created, 'DD.MM.YYYY') AS created_fmt
        FROM image
        WHERE is_published = true
        AND is_deleted = false
        AND created BETWEEN '{created_since}' AND '{created_until}'
        {order_clause(order)}
        LIMIT {limit} OFFSET {offset}
    """
    count = f"""
        SELECT COUNT(*)
        FROM image
        WHERE is_published = true
        AND is_deleted = false
        AND created BETWEEN '{created_since}' AND '{created_until}'
    """
    return {
        "rows": (
            dict(i) | {"file_name": os.path.basename(i.get("image_url", ""))}
            for i in db.session.execute(query).mappings().all()
        )
    } | dict(db.session.execute(count).mappings().fetchone())


def comments(created_since, created_until, order, limit, offset, **kwargs):
    query = f"""
        SELECT
        id, created, "text", creator_id, poi_id,
        to_char(created, 'DD.MM.YYYY') AS created_fmt
        FROM comment
        WHERE is_published = true
        AND is_deleted = false
        AND created BETWEEN '{created_since}' AND '{created_until}'
        {order_clause(order)}
        LIMIT {limit} OFFSET {offset}
    """
    count = f"""
        SELECT COUNT(*)
        FROM comment
        WHERE is_published = true
        AND is_deleted = false
        AND created BETWEEN '{created_since}' AND '{created_until}'
    """
    return {"rows": db.session.execute(query).mappings().all()} | dict(
        db.session.execute(count).mappings().fetchone()
    )


def cat_choices():
    query = f"""
        SELECT id, "name"
        FROM category
        WHERE is_published = true
        AND is_deleted = false
        ORDER BY "name"
    """
    return db.session.execute(query).mappings().all()
