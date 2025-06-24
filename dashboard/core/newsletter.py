import requests
from flask import current_app
from sqlalchemy import text

from ..extensions import db


def subscribe(nl_url, nl_list_id, nl_api_key):
    query = """
        SELECT
        TRIM(first_name || ' ' || last_name) as "name",
        email
        FROM creator
        WHERE is_deleted = FALSE
        AND created > date('now', '-1 day')
        AND UPPER(TRIM(email)) NOT LIKE UPPER('%@privaterelay.appleid.com')
        AND UPPER(TRIM(email)) NOT LIKE UPPER('%@users.mapotic.com')
    """
    creators = db.session.execute(text(query)).mappings().all()

    if not creators:
        current_app.logger.info("No new creators")
        return

    current_app.logger.info(f"Subscribing {len(creators)} new creators")

    for c in creators:
        body = {
            "list": nl_list_id,
            "api_key": nl_api_key,
            "email": c["email"],
        }
        if name := c["name"]:
            body |= {"name": name}

        requests.post(f"{nl_url}/subscribe", data=body)


def unsubscribe(nl_url, nl_list_id, nl_api_key):
    query = """
        SELECT email
        FROM creator
        WHERE is_deleted = TRUE
        AND modified > date('now', '-1 day')
    """
    creators = db.session.execute(text(query)).mappings().all()

    if not creators:
        current_app.logger.info("No deleted creators")
        return

    current_app.logger.info(f"Unsubscribing {len(creators)} deleted creators")

    for c in creators:
        body = {
            "list": nl_list_id,
            "api_key": nl_api_key,
            "email": c["email"],
        }

        requests.post(f"{nl_url}/unsubscribe", data=body)


def update():
    nl_url = current_app.config.get("NEWSLETTER_URL")
    nl_list_id = current_app.config.get("NEWSLETTER_LIST_ID")
    nl_api_key = current_app.config.get("NEWSLETTER_API_KEY")

    current_app.logger.info("Running newsletter update")
    subscribe(nl_url, nl_list_id, nl_api_key)
    unsubscribe(nl_url, nl_list_id, nl_api_key)


def dump_emails():
    query = """
        SELECT
        TRIM(first_name || ' ' || last_name) as "name",
        email,
        strftime('%Y-%m-%d', created)
        FROM creator
        WHERE is_deleted = FALSE
        ORDER BY created DESC
    """
    for c in db.session.execute(text(query)).all():
        print(",".join(c))
