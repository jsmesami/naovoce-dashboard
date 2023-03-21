ZONES_SELECT = """
    SELECT
        z.id, z.created, z.modified, z.name,
        u.email as author,
        to_char(z.created, 'DD.MM.YYYY') AS created_fmt,
        to_char(z.modified, 'DD.MM.YYYY') AS modified_fmt,
        string_agg(cz.name_2::text, '; ') AS districts
    FROM zone z
    LEFT JOIN "user" u ON u.id = z.author_id
    LEFT JOIN cz_2 cz ON ST_Intersects(cz.geom, z.area)
    GROUP BY z.id, z.modified, u.email
    ORDER BY z.modified DESC
"""

ZONE_GET = """
    SELECT
        z.id, z.created, z.modified, z.name, z.area,
        u.email as author,
        to_char(z.created, 'DD.MM.YYYY') AS created_fmt,
        to_char(z.modified, 'DD.MM.YYYY') AS modified_fmt,
        ST_AsGeoJSON(z.area) AS area_geojson,
        string_agg(cz.name_2::text, '; ') AS districts
    FROM zone z
    LEFT JOIN "user" u ON u.id = z.author_id
    LEFT JOIN cz_2 cz ON ST_Intersects(cz.geom, z.area)
    WHERE z.id = :zone_id
    GROUP BY z.id, u.email
"""

ZONE_UPDATE = """
    UPDATE zone
    SET author_id = :author,
        "name" = :name,
        area = :area,
        modified = now()
    WHERE id = :zone_id
"""

ZONE_DELETE = """
    DELETE FROM zone
    WHERE id = :zone_id
"""

POIS_IN_ZONES = """
    WITH excluded_categories AS (
        SELECT id
        FROM category cat
        WHERE cat.name IN ('Sady', 'Ovocné trasy')
           OR cat.is_published = false
           OR cat.is_deleted = true
    )
    SELECT
        poi.id, poi.created,
        category.name AS category_name,
        TRIM(CONCAT(first_name, ' ', last_name)) as creator_name,
        creator.email as creator_email,
        zone.name as zone_name,
        to_char(poi.created, 'DD.MM.YYYY') AS created_fmt
    FROM poi
    JOIN zone ON ST_Intersects(poi.position, zone.area)
    LEFT JOIN creator ON creator.id = poi.creator_id
    LEFT JOIN category ON category.id = poi.category_id
    WHERE poi.is_published = true
        AND poi.is_deleted = false
        AND poi.category_id NOT IN (SELECT id FROM excluded_categories)
    ORDER BY category_name, poi.created DESC
"""
