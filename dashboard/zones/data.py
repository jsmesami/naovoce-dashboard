ZONES_SELECT = """
    SELECT
        z.id, z.created, z.modified, z.name,
        u.email as author,
        strftime('%d.%m.%Y', z.created) AS created_fmt,
        strftime('%d.%m.%Y', z.modified) AS modified_fmt,
        GROUP_CONCAT(cz.name_2, '; ') AS districts
    FROM zone z
    LEFT JOIN "user" u ON u.id = z.author_id
    LEFT JOIN cz_2 cz ON Intersects(cz.geometry, z.area)
    GROUP BY z.id, z.modified, u.email
    ORDER BY z.modified DESC
"""

ZONE_GET = """
    SELECT
        z.id, z.created, z.modified, z.name, z.area,
        u.email as author,
        strftime('%d.%m.%Y', z.created) AS created_fmt,
        strftime('%d.%m.%Y', z.modified) AS modified_fmt,
        AsGeoJSON(z.area) AS area_geojson,
        GROUP_CONCAT(cz.name_2, '; ') AS districts
    FROM zone z
    LEFT JOIN "user" u ON u.id = z.author_id
    LEFT JOIN cz_2 cz ON Intersects(cz.geometry, z.area)
    WHERE z.id = :zone_id
    GROUP BY z.id, u.email
"""

ZONE_UPDATE = """
    UPDATE zone
    SET author_id = :author,
        "name" = :name,
        area = :area,
        modified = datetime('now')
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
           OR cat.is_published = FALSE
           OR cat.is_deleted = TRUE
    )
    SELECT
        poi.id, poi.created,
        category.name AS category_name,
        TRIM(first_name || ' ' || last_name) as creator_name,
        creator.email as creator_email,
        zone.name as zone_name,
        strftime('%d.%m.%Y', poi.created) AS created_fmt
    FROM poi
    JOIN zone ON Intersects(poi.position, zone.area)
    LEFT JOIN creator ON creator.id = poi.creator_id
    LEFT JOIN category ON category.id = poi.category_id
    WHERE poi.is_published = TRUE
        AND poi.is_deleted = FALSE
        AND poi.category_id NOT IN (SELECT id FROM excluded_categories)
    ORDER BY category_name, poi.created DESC
"""
