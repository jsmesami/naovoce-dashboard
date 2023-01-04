import contextlib
import re
from datetime import datetime


def select_keys(d, keys):
    return {key: d[key] for key in keys if key in d}


def str_to_datetime(s):
    dt_match = r"\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}"
    dt_format = "%Y-%m-%d %H:%M:%S"

    if match := re.search(dt_match, s):
        return datetime.strptime(match.group(0), dt_format)


def latlng_to_point(lat, lng):
    with contextlib.suppress(ValueError, TypeError):
        return f"POINT({float(lng)} {float(lat)})"


def str_to_bool(s):
    return s == "t"


def str_to_int(s):
    with contextlib.suppress(ValueError, TypeError):
        return int(s)


def identity(d):
    return d
