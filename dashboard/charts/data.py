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
