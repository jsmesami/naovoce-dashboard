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
        FROM category;
    """,
    "users": """
        SELECT
        id, created, first_name, last_name, email, last_visit
        FROM creator;
    """,
    "pois": """
        SELECT
        id, created, display_count,
        ST_X(position) as lng,
        ST_Y(position) as lat,
        is_published, creator_id, category_id
        FROM poi;
    """,
    "images": """
        SELECT
        id, created, image_url, is_published, creator_id, poi_id
        FROM image;
    """,
    "comments": """
        SELECT
        id, created, "text", is_published, creator_id, poi_id
        FROM comment;
    """,
}
