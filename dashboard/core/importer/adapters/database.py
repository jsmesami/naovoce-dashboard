from . import identity, latlng_to_point


def poi_adapter(d):
    ret = {
        "position": latlng_to_point(d["lat"], d["lng"]),
    }
    d.pop("lat", None)
    d.pop("lng", None)
    return d | ret


ADAPTERS = {
    "categories": identity,
    "users": identity,
    "pois": poi_adapter,
    "images": identity,
    "comments": identity,
}
