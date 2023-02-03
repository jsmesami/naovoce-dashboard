import re
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import request, session

from . import data

DEFAULT_SECTION = "creators"
DEFAULT_LIMIT = 40
DEFAULT_ORDER = "created_desc"
MIN_CREATED = lambda: str(
    datetime(year=2013, month=1, day=1, tzinfo=ZoneInfo("Europe/Prague")).date()
)
MAX_CREATED = lambda: str(datetime.now(ZoneInfo("Europe/Prague")).date())
MIN_VISITED = MIN_CREATED
MAX_VISITED = MAX_CREATED

SECTIONS = ("creators", "categories", "pois", "images", "comments")
ROWS_FETCHERS = (
    data.creators_rows,
    data.categories_rows,
    data.pois_rows,
    data.images_rows,
    data.comments_rows,
)
COUNT_FETCHERS = (
    data.creators_count,
    data.categories_count,
    data.pois_count,
    data.images_count,
    data.comments_count,
)
SECTION_ROWS_FETCHERS = dict(zip(SECTIONS, ROWS_FETCHERS))
SECTION_COUNT_FETCHERS = dict(zip(SECTIONS, COUNT_FETCHERS))

SECTION_FIELDS = {
    "creators": (
        "id",
        "created",
        "first_name",
        "last_name",
        "email",
        "last_visit",
        "n_pois",
        "n_images",
        "n_comments",
    ),
    "categories": (
        "id",
        "created",
        "name",
        "n_pois",
    ),
    "pois": (
        "id",
        "created",
        "category_name",
        "display_count",
        "creator_id",
        "category_id",
        "n_images",
        "n_comments",
    ),
    "images": (
        "id",
        "created",
        "creator_id",
        "poi_id",
    ),
    "comments": (
        "id",
        "created",
        "text",
        "creator_id",
        "poi_id",
    ),
}


def get_param(key, default, adapter):
    if (ret := request.args.get(key)) is None:
        return default

    try:
        ret = adapter(ret, default)
    except (ValueError, TypeError):
        ret = default

    return ret


def getset_param(key, default, adapter):
    if (ret := request.args.get(key)) is None:
        ret = session.get(key, default)

    try:
        ret = adapter(ret, default)
    except (ValueError, TypeError):
        ret = default

    session[key] = ret
    return ret


def identity(text, _default):
    return text


def guard_bool(boolean, default):
    if type(boolean) == str:
        return boolean.lower() in ("true", "t")
    elif type(boolean) == bool:
        return boolean

    return default


def guard_posint(n, default):
    if (n := int(n)) > 0:
        return n

    return default


def guard_section(section, default):
    if match := re.match(rf"({'|'.join(SECTIONS)})", section):
        return match.group(0)

    return default


def guard_category(cat_ids):
    def closure(n, default):
        if (n := int(n)) in cat_ids:
            return n
        else:
            return default

    return closure


def guard_date(date, _default):
    return str(datetime.strptime(date, "%Y-%m-%d").date())


def guard_offset(n, default):
    ret = int(n)
    return ret if ret >= 0 else default


def guard_limit(n, default):
    ret = int(n)
    return ret if 0 <= ret <= 500 else default


def guard_order(section):
    def closure(order, default):
        fields = SECTION_FIELDS.get(section)
        if match := re.match(rf"({'|'.join(fields)})(_asc|_desc)", order):
            field, direction = match.groups()
            return f"{field}{direction}"

        return default

    return closure


def next_order(field, current_order):
    f, direction = current_order.rsplit("_", maxsplit=1)
    if f == field:
        next_dir = "desc" if direction == "asc" else "asc"
        return f"{field}_{next_dir}"

    return f"{field}_desc"


def reset_filters(section):
    for k in list(session.keys()):
        if k.startswith(section):
            session.pop(k)


def section_params(section, show_controls):
    params = {
        "section": section,
    }

    if get_param(f"{section}_reset_filters", False, guard_bool):
        reset_filters(section)

    offset = getset_param(f"{section}_offset", 0, guard_offset)
    limit = getset_param(f"{section}_limit", DEFAULT_LIMIT, guard_limit)
    order = getset_param(f"{section}_order", DEFAULT_ORDER, guard_order(section))

    created_since = getset_param(f"{section}_created_since", MIN_CREATED(), guard_date)
    created_until = getset_param(f"{section}_created_until", MAX_CREATED(), guard_date)

    params |= {
        "offset": offset,
        "limit": limit,
        "order": order,
        "show_controls": show_controls,
        "created_since": created_since,
        "created_until": created_until,
        "created_min": MIN_CREATED(),
        "created_max": MAX_CREATED(),
    }

    if section == "pois":
        id_filter = get_param("pois_id_filter", 0, guard_posint)
        choices = data.cat_choices()
        cat_ids = (ch["id"] for ch in choices)
        cat_id_filter = getset_param("pois_cat_id_filter", 0, guard_category(cat_ids))
        params |= {
            "id_filter": id_filter,
            "cat_choices": choices,
            "cat_id_filter": cat_id_filter,
        }

    if section == "creators":
        search = getset_param("creators_search", "", identity)
        id_filter = get_param("creators_id_filter", 0, guard_posint)
        visited_since = getset_param(
            "creators_visited_since", MIN_VISITED(), guard_date
        )
        visited_until = getset_param(
            "creators_visited_until", MAX_VISITED(), guard_date
        )
        params |= {
            "search": search,
            "id_filter": id_filter,
            "visited_since": visited_since,
            "visited_until": visited_until,
            "visited_min": MIN_VISITED(),
            "visited_max": MAX_VISITED(),
        }

    return params
