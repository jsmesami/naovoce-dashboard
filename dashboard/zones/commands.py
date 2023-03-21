from flask import current_app, render_template
from sqlalchemy import text

from ..extensions import db
from ..utils.email import send_email
from . import data, zones


def dump_pois():
    return [
        {
            "id": poi.id,
            "zone": poi.zone_name,
            "category": poi.category_name,
            "creator": f"{poi.creator_name} <{poi.creator_email or 'no email'}>".strip(),
            "created": poi.created_fmt,
        }
        for poi in db.session.execute(text(data.POIS_IN_ZONES)).mappings().all()
    ]


@zones.cli.command("check-zones")
def check_zones():
    if pois := dump_pois():
        send_email(
            current_app,
            recipient="team@na-ovoce.cz",
            subject=render_template("zones/email_subject.txt", num=len(pois)),
            body=render_template("zones/email_body.txt", pois=pois),
        )
