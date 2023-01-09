import os

from ..extensions import db


def get_order_clause(order):
    return " ".join(order.rsplit("_", maxsplit=1))


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
        ORDER BY {order}
        LIMIT :limit OFFSET :offset;
    """.format(
        order=get_order_clause(args.get("order"))
    )
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
        ORDER BY {order}
        LIMIT :limit OFFSET :offset;
    """.format(
        order=get_order_clause(args.get("order"))
    )
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
        cat.name AS category_name,
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
        ORDER BY {order}
        LIMIT :limit OFFSET :offset;
    """.format(
        order=get_order_clause(args.get("order"))
    )
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
        ORDER BY {order}
        LIMIT :limit OFFSET :offset;
    """.format(
        order=get_order_clause(args.get("order"))
    )
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
        ORDER BY {order}
        LIMIT :limit OFFSET :offset;
    """.format(
        order=get_order_clause(args.get("order"))
    )
    count = """
        SELECT COUNT(*)
        FROM comment
        WHERE is_published = true
    """
    return {"rows": db.session.execute(query, args).mappings().all()} | dict(
        db.session.execute(count).mappings().fetchone()
    )
