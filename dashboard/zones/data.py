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
