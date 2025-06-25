import contextlib
import re
from datetime import datetime


def adapt_datetime(s):
    dt_match = r"\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}"
    dt_format = "%Y-%m-%d %H:%M:%S"

    if match := re.search(dt_match, s or ""):
        return datetime.strptime(match.group(0), dt_format)


def latlng_to_point(lat, lng):
    with contextlib.suppress(ValueError, TypeError):
        return (
            f"POINT({float(format(float(lat), "f"))} {float(format(float(lng), "f"))})"
        )


def adapt_bool(s):
    return 1 if s == "t" else 0


def adapt_int(s):
    with contextlib.suppress(ValueError, TypeError):
        return int(s)
