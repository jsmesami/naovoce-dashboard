from collections import defaultdict
from itertools import accumulate
from operator import itemgetter

from sqlalchemy import text

from ..extensions import db


def monthly_gains_chart():
    poi_query = """
        WITH excluded_categories AS (
            SELECT id FROM category cat WHERE cat.name IN ('Sady', 'Ovocné trasy')
        )
        SELECT
        strftime('%Y-%m-01', created) AS created_in_month,
        "'" || CAST(strftime('%m', created) AS INTEGER) || '/' || substr(strftime('%Y', created), 3, 2) || "'" AS formatted_month,
        COUNT(id) AS count
        FROM poi
        WHERE is_published = TRUE
        AND is_deleted = FALSE
        AND created >= '2015-01-01'
        AND poi.category_id NOT IN (SELECT id FROM excluded_categories)
        GROUP BY created_in_month
        ORDER BY created_in_month
    """
    pois = db.session.execute(text(poi_query)).all()
    pois_counts = [cnt for _dat, _fmt, cnt in pois]

    creator_query = """
        SELECT
        strftime('%Y-%m-01', created) AS created_in_month,
        "'" || CAST(strftime('%m', created) AS INTEGER) || '/' || substr(strftime('%Y', created), 3, 2) || "'" AS formatted_month,
        COUNT(id) AS count
        FROM creator
        WHERE is_deleted = FALSE
        AND created >= '2015-01-01'
        GROUP BY created_in_month
        ORDER BY created_in_month
    """
    creators = db.session.execute(text(creator_query)).all()
    creators_counts = [cnt for _dat, _fmt, cnt in creators]

    return {
        "months": ", ".join(fmt for _dat, fmt, _cnt in creators),
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
            OR cat.is_published = FALSE
            OR cat.is_deleted = TRUE
        )
        SELECT
        strftime('%Y-%m-01', poi.created) AS created_in_month,
        "'" || CAST(strftime('%m', poi.created) AS INTEGER) || '/' || substr(strftime('%Y', poi.created), 3, 2) || "'" AS formatted_month,
        cat.name AS category_name,
        COUNT(poi.id) AS count
        FROM poi
        LEFT JOIN category cat ON cat.id = poi.category_id
        WHERE poi.is_published = TRUE
        AND poi.is_deleted = FALSE
        AND poi.created >= '2015-01-01'
        AND poi.category_id NOT IN (SELECT id FROM excluded_categories)
        GROUP BY created_in_month, category_name
    """
    pois = db.session.execute(text(query)).all()

    months = sorted({dat for dat, _fmt, _cat, _cnt in pois})
    formatted_months = {dat: fmt for dat, fmt, _cat, _cnt in pois}
    months_index = {mon: idx for idx, mon in enumerate(months)}

    cat_counts = defaultdict(int)
    for _dat, _fmt, cat, cnt in pois:
        cat_counts[cat] += cnt

    categories = [item[0] for item in sorted(cat_counts.items(), key=itemgetter(1))]
    categories_index = {cat: idx for idx, cat in enumerate(categories)}

    matrix = (
        (months_index[dat], categories_index[cat], cnt or "-")
        for dat, _fmt, cat, cnt in pois
    )

    return {
        "months": ", ".join(formatted_months[dat] for dat in months),
        "categories": ", ".join(f"'{cat}'" for cat in categories),
        "matrix": ", ".join(f"[{x}, {y}, {c}]" for x, y, c in matrix),
    }


def cz_geojson():
    query = """
        SELECT json_object(
            'type', 'FeatureCollection',
            'features', json_group_array(
                json_object(
                    'type', 'Feature',
                    'properties', json_object(
                        'name', name_1,
                        'pk_uid', pk_uid
                    ),
                    'geometry', json(AsGeoJSON(geometry))
                )
            )
        )
        FROM cz_1
    """
    ret, *_ = db.session.execute(text(query)).fetchone()
    return ret


def cz_area_counts():
    query = """
        SELECT area.name_1 AS name, COUNT(poi.position) AS value
        FROM cz_1 AS area
            LEFT JOIN poi
            ON ST_Within(poi.position, area.geometry)
        WHERE poi.is_published = TRUE
          AND poi.is_deleted = FALSE
        GROUP BY area.pk_uid;
    """
    return db.session.execute(text(query)).mappings().all()
