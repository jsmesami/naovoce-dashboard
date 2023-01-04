from . import latlng_to_point, str_to_bool, str_to_datetime, str_to_int


def category_adapter(d):
    return {
        "id": str_to_int(d["id"]),
        "created": str_to_datetime(d["created"]),
        "name": d["name_cs"],
        "is_published": str_to_bool(d["is_published"]),
    }


def creator_adapter(d):
    return {
        "id": str_to_int(d["id"]),
        "created": str_to_datetime(d["created"]),
        "first_name": d["first_name"],
        "last_name": d["last_name"],
        "email": d["email"],
        "last_visit": str_to_datetime(d["last_visit"]),
    }


def poi_adapter(d):
    return {
        "id": str_to_int(d["id"]),
        "created": str_to_datetime(d["created"]),
        "position": latlng_to_point(d["lat"], d["lng"]),
        "display_count": str_to_int(d["display_count"]),
        "is_published": str_to_bool(d["is_published"]),
        "creator_id": str_to_int(d["creator_id"]),
        "category_id": str_to_int(d["category_id"]),
    }


def image_adapter(d):
    return {
        "id": str_to_int(d["id"]),
        "created": str_to_datetime(d["created"]),
        "is_published": str_to_bool(d["is_published"]),
        "image_url": d["image_url"],
        "creator_id": str_to_int(d["creator_id"]),
        "poi_id": str_to_int(d["geo_id"]),
    }


def comment_adapter(d):
    return {
        "id": str_to_int(d["id"]),
        "created": str_to_datetime(d["created"]),
        "text": d["text"],
        "is_published": str_to_bool(d["is_published"]),
        "creator_id": str_to_int(d["creator_id"]),
        "poi_id": str_to_int(d["geo_id"]),
    }


ADAPTERS = {
    "categories": category_adapter,
    "users": creator_adapter,
    "pois": poi_adapter,
    "images": image_adapter,
    "comments": comment_adapter,
}
