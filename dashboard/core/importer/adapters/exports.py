from . import adapt_bool, adapt_datetime, adapt_int, latlng_to_point


def category_adapter(d):
    return {
        "id": adapt_int(d["id"]),
        "created": adapt_datetime(d["created"]),
        "name": d["name_cs"].strip(),
        "is_published": adapt_bool(d["is_published"]),
    }


def creator_adapter(d):
    return {
        "id": adapt_int(d["id"]),
        "created": adapt_datetime(d["created"]),
        "first_name": d["first_name"].strip(),
        "last_name": d["last_name"].strip(),
        "email": d["email"],
        "last_visit": adapt_datetime(d["last_visit"]),
    }


def poi_adapter(d):
    return {
        "id": adapt_int(d["id"]),
        "created": adapt_datetime(d["created"]),
        "position": latlng_to_point(d["lat"], d["lng"]),
        "display_count": adapt_int(d["display_count"]),
        "is_published": adapt_bool(d["is_published"]),
        "creator_id": adapt_int(d["creator_id"]),
        "category_id": adapt_int(d["category_id"]),
    }


def image_adapter(d):
    return {
        "id": adapt_int(d["id"]),
        "created": adapt_datetime(d["created"]),
        "is_published": adapt_bool(d["is_published"]),
        "image_url": d["image_url"],
        "creator_id": adapt_int(d["creator_id"]),
        "poi_id": adapt_int(d["geo_id"]),
    }


def comment_adapter(d):
    return {
        "id": adapt_int(d["id"]),
        "created": adapt_datetime(d["created"]),
        "text": d["text"],
        "is_published": adapt_bool(d["is_published"]),
        "creator_id": adapt_int(d["creator_id"]),
        "poi_id": adapt_int(d["geo_id"]),
    }


ADAPTERS = {
    "categories": category_adapter,
    "users": creator_adapter,
    "pois": poi_adapter,
    "images": image_adapter,
    "comments": comment_adapter,
}
