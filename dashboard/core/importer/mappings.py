from .. import models

EXPORT_GROUPS = ("categories", "users", "pois", "images", "comments")

EXPORT_GROUP_MODELS = {
    "categories": models.Category,
    "users": models.Creator,
    "pois": models.POI,
    "images": models.Image,
    "comments": models.Comment,
}

EXPORT_GROUP_QUERIES = {
    "categories": """
        SELECT
        id, created, "name", is_published
        FROM category
        WHERE is_deleted = false
    """,
    "users": """
        SELECT
        id, created, first_name, last_name, email, last_visit
        FROM creator
        WHERE is_deleted = false
    """,
    "pois": """
        SELECT
        id, created, display_count,
        ST_X(position) AS lng,
        ST_Y(position) AS lat,
        is_published, creator_id, category_id
        FROM poi
        WHERE is_deleted = false
    """,
    "images": """
        SELECT
        id, created, image_url, is_published, creator_id, poi_id
        FROM image
        WHERE is_deleted = false
    """,
    "comments": """
        SELECT
        id, created, "text", is_published, creator_id, poi_id
        FROM comment
        WHERE is_deleted = false
    """,
}
