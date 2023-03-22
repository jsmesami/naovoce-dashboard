import logging

from flask import current_app, render_template
from sqlalchemy import text

from ..extensions import db
from ..utils.commands import wrap_command
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
@wrap_command(current_app)
def check_zones():
    """Checks if there are POIs within Zones, executed daily with Cron"""
    current_app.logger.setLevel(logging.INFO)
    current_app.logger.info("Checking Zones")

    if pois := dump_pois():
        num_pois = len(pois)
        current_app.logger.info(f"{num_pois} POIs found within Zones, sending email")
        send_email(
            current_app,
            recipient="team@na-ovoce.cz",
            subject=render_template("zones/email_subject.txt", num=num_pois),
            body=render_template("zones/email_body.txt", pois=pois),
        )
    else:
        current_app.logger.info("No POIs found within Zones")
