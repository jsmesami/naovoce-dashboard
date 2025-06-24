import contextlib
import re


def select_keys(d, keys):
    return {key: d[key] for key in keys if key in d}


def str_to_datetime(s):
    dt_match = r"\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}"

    if re.search(dt_match, s):
        return s


def latlng_to_point(lat, lng):
    with contextlib.suppress(ValueError, TypeError):
        return (
            f"POINT({float(format(float(lat), "f"))} {float(format(float(lng), "f"))})"
        )


def str_to_bool(s):
    return s == "t"


def str_to_int(s):
    with contextlib.suppress(ValueError, TypeError):
        return int(s)


def identity(d):
    return d
