import requests
from flask import current_app

from ..extensions import db


def update():
    nl_url = current_app.config.get("NEWSLETTER_URL")
    nl_list_id = current_app.config.get("NEWSLETTER_LIST_ID")
    nl_api_key = current_app.config.get("NEWSLETTER_API_KEY")

    query = """
        SELECT
        TRIM(CONCAT(first_name, ' ', last_name)) as "name",
        email
        FROM creator
        WHERE is_deleted = false
        AND created > current_date - 1
    """
    creators = db.session.execute(query).mappings().all()

    current_app.logger.info("Running newsletter update")

    if not creators:
        current_app.logger.info("No new creators")
        return

    current_app.logger.info(f"Updating {len(creators)} creators")

    for c in creators:
        body = {
            "list": nl_list_id,
            "api_key": nl_api_key,
            "email": c["email"],
        }
        if name := c["name"]:
            body |= {"name": name}

        requests.post(nl_url, data=body)


def dump_emails():
    query = """
        SELECT
        TRIM(CONCAT(first_name, ' ', last_name)) as "name",
        email,
        to_char(created, 'YYYY-MM-DD')
        FROM creator
        WHERE is_deleted = false
        ORDER BY created DESC
    """
    for c in db.session.execute(query).all():
        print(",".join(c))
