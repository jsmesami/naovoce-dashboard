from . import adapt_datetime, latlng_to_point


def categories_adapter(d):
    return {
        **d,
        "created": adapt_datetime(d["created"]),
    }


def users_adapter(d):
    return {
        **d,
        "created": adapt_datetime(d["created"]),
        "last_visit": adapt_datetime(d["last_visit"]),
    }


def poi_adapter(d):
    ret = {
        "position": latlng_to_point(d["lat"], d["lng"]),
        "created": adapt_datetime(d["created"]),
    }
    d.pop("lat", None)
    d.pop("lng", None)
    return {
        **d,
        **ret,
    }


def images_adapter(d):
    return {
        **d,
        "created": adapt_datetime(d["created"]),
    }


def comments_adapter(d):
    return {
        **d,
        "created": adapt_datetime(d["created"]),
    }


ADAPTERS = {
    "categories": categories_adapter,
    "users": users_adapter,
    "pois": poi_adapter,
    "images": images_adapter,
    "comments": comments_adapter,
}
