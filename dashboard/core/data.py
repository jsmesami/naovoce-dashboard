import os
from collections import defaultdict
from itertools import accumulate
from operator import itemgetter

from sqlalchemy import text

from ..extensions import db


def order_clause(order):
    return "ORDER BY " + " ".join(order.rsplit("_", maxsplit=1))


def pagination_clause(limit, offset):
    if not limit:
        return ""

    return f"LIMIT {limit} OFFSET {offset}"


def id_filter_clause(id_filter, prefix=None):
    return f"AND {prefix or ''}id = {id_filter}" if id_filter else ""


def creator_search_clause(search):
    if not search:
        return ""

    return """
        AND (
            email ILIKE '%' || :search || '%'
            OR first_name ILIKE '%' || :search || '%'
            OR last_name ILIKE '%' || :search || '%'
        )
    """


def creators_rows(
    created_since,
    created_until,
    visited_since,
    visited_until,
    order,
    id_filter,
    search,
    limit=None,
    offset=0,
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
        {pagination_clause(limit, offset)}
    """
    return dict(
        rows=db.session.execute(text(query), dict(search=f"%{search}%"))
        .mappings()
        .all()
    )


def creators_count(created_since, created_until, id_filter, search, **kwargs):
    query = f"""
        SELECT COUNT(*)
        FROM creator
        WHERE is_deleted = false
        AND created BETWEEN '{created_since}' AND '{created_until}'
        {id_filter_clause(id_filter)}
        {creator_search_clause(search)}
    """
    return dict(
        db.session.execute(text(query), dict(search=f"%{search}%"))
        .mappings()
        .fetchone()
    )


def categories_rows(
    created_since, created_until, order, limit=None, offset=0, **kwargs
):
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
        {pagination_clause(limit, offset)}
    """
    return dict(rows=db.session.execute(text(query)).mappings().all())


def categories_count(created_since, created_until, **kwargs):
    query = f"""
        SELECT COUNT(*)
        FROM category
        WHERE is_published = true
        AND is_deleted = false
        AND created BETWEEN '{created_since}' AND '{created_until}'
    """
    return dict(db.session.execute(text(query)).mappings().fetchone())


def pois_rows(
    created_since,
    created_until,
    order,
    cat_id_filter,
    id_filter,
    limit=None,
    offset=0,
    **kwargs,
):
    query = f"""
        SELECT
        poi.id, poi.created, poi.display_count, poi.creator_id, poi.category_id,
        cat.name AS category_name,
        to_char(poi.created, 'DD.MM.YYYY') AS created_fmt,
        ST_X(poi.position) AS lat,
        ST_Y(poi.position) AS lng,
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
        {id_filter_clause(cat_id_filter, 'category_')}
        {id_filter_clause(id_filter, 'poi.')}
        {order_clause(order)}
        {pagination_clause(limit, offset)}
    """
    return dict(rows=db.session.execute(text(query)).mappings().all())


def pois_count(created_since, created_until, cat_id_filter, id_filter, **kwargs):
    query = f"""
        SELECT COUNT(*)
        FROM poi
        WHERE is_published = true
        AND is_deleted = false
        AND created BETWEEN '{created_since}' AND '{created_until}'
        {id_filter_clause(cat_id_filter, 'category_')}
        {id_filter_clause(id_filter, 'poi.')}
    """
    return dict(db.session.execute(text(query)).mappings().fetchone())


def images_rows(created_since, created_until, order, limit=None, offset=0, **kwargs):
    query = f"""
        SELECT
        id, created, image_url, creator_id, poi_id,
        to_char(created, 'DD.MM.YYYY') AS created_fmt
        FROM image
        WHERE is_published = true
        AND is_deleted = false
        AND created BETWEEN '{created_since}' AND '{created_until}'
        {order_clause(order)}
        {pagination_clause(limit, offset)}
    """
    return dict(
        rows=(
            dict(i) | {"file_name": os.path.basename(i.get("image_url", ""))}
            for i in db.session.execute(text(query)).mappings().all()
        )
    )


def images_count(created_since, created_until, **kwargs):
    query = f"""
        SELECT COUNT(*)
        FROM image
        WHERE is_published = true
        AND is_deleted = false
        AND created BETWEEN '{created_since}' AND '{created_until}'
    """
    return dict(db.session.execute(text(query)).mappings().fetchone())


def comments_rows(created_since, created_until, order, limit=None, offset=0, **kwargs):
    query = f"""
        SELECT
        id, created, "text", creator_id, poi_id,
        to_char(created, 'DD.MM.YYYY') AS created_fmt
        FROM comment
        WHERE is_published = true
        AND is_deleted = false
        AND created BETWEEN '{created_since}' AND '{created_until}'
        {order_clause(order)}
        {pagination_clause(limit, offset)}
    """
    return dict(rows=db.session.execute(text(query)).mappings().all())


def comments_count(created_since, created_until, **kwargs):
    query = f"""
        SELECT COUNT(*)
        FROM comment
        WHERE is_published = true
        AND is_deleted = false
        AND created BETWEEN '{created_since}' AND '{created_until}'
    """
    return dict(db.session.execute(text(query)).mappings().fetchone())


def cat_choices():
    query = f"""
        SELECT id, "name"
        FROM category
        WHERE is_published = true
        AND is_deleted = false
        ORDER BY "name"
    """
    return db.session.execute(text(query)).mappings().all()


def monthly_gains_chart():
    poi_query = """
        WITH excluded_categories AS (
            SELECT id FROM category cat WHERE cat.name IN ('Sady', 'Ovocné trasy')
        )
        SELECT
        DATE_TRUNC('month', created) AS created_in_month,
        COUNT(id) AS count
        FROM poi
        WHERE is_published = true
        AND is_deleted = false
        AND created >= '2015-01-01'
        AND poi.category_id NOT IN (SELECT id FROM excluded_categories)
        GROUP BY created_in_month
        ORDER BY created_in_month
    """
    pois = db.session.execute(text(poi_query)).all()
    pois_counts = [cnt for _dat, cnt in pois]

    creator_query = """
        SELECT
        DATE_TRUNC('month', created) AS created_in_month,
        COUNT(id) AS count
        FROM creator
        WHERE is_deleted = false
        AND created >= '2015-01-01'
        GROUP BY DATE_TRUNC('month', created)
        ORDER BY created_in_month
    """
    creators = db.session.execute(text(creator_query)).all()
    creators_counts = [cnt for _dat, cnt in creators]

    return {
        "months": ", ".join(dat.strftime("'%-m/%-y'") for dat, _cnt in creators),
        "creators": ", ".join(str(i) for i in creators_counts),
        "creators_cum": ", ".join(str(i) for i in accumulate(creators_counts)),
        "pois": ", ".join(str(i) for i in pois_counts),
        "pois_cum": ", ".join(str(i) for i in accumulate(pois_counts)),
    }


def monthly_pois_chart():
    query = """
        WITH excluded_categories AS (
            SELECT id
            FROM category cat
            WHERE cat.name IN ('Sady', 'Ovocné trasy')
            OR cat.is_published = false
            OR cat.is_deleted = true
        )
        SELECT
        DATE_TRUNC('month', poi.created) AS created_in_month,
        cat.name AS category_name,
        COUNT(poi.id) AS count
        FROM poi
        LEFT JOIN category cat ON cat.id = poi.category_id
        WHERE poi.is_published = true
        AND poi.is_deleted = false
        AND poi.created >= '2015-01-01'
        AND poi.category_id NOT IN (SELECT id FROM excluded_categories)
        GROUP BY created_in_month, category_name
    """
    pois = db.session.execute(text(query)).all()

    months = sorted({dat for dat, _cat, _cnt in pois})
    months_index = {mon: idx for idx, mon in enumerate(months)}

    cat_counts = defaultdict(int)
    for _dat, cat, cnt in pois:
        cat_counts[cat] += cnt

    categories = [item[0] for item in sorted(cat_counts.items(), key=itemgetter(1))]
    categories_index = {cat: idx for idx, cat in enumerate(categories)}

    matrix = (
        (months_index[dat], categories_index[cat], cnt or "-") for dat, cat, cnt in pois
    )

    return {
        "months": ", ".join(dat.strftime("'%-m/%-y'") for dat in months),
        "categories": ", ".join(f"'{cat}'" for cat in categories),
        "matrix": ", ".join(f"[{x}, {y}, {c}]" for x, y, c in matrix),
    }


def cz_geojson():
    query = """
        SELECT json_build_object(
            'type', 'FeatureCollection',
            'features', json_agg(ST_AsGeoJSON(t.*)::json)
        )
        FROM (
            SELECT name_1 as name, geom
            FROM cz_1
        ) AS t;
    """
    ret, *_ = db.session.execute(text(query)).fetchone()
    return ret


def cz_area_counts():
    query = """
        SELECT area.name_1 AS name, count(poi.position) AS value
        FROM poi
        RIGHT JOIN cz_1 area ON st_within(poi.position, area.geom)
        WHERE poi.is_published = true
        AND poi.is_deleted = false
        GROUP BY area.gid;
    """
    return db.session.execute(text(query)).mappings().all()
