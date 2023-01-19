import requests
from flask import current_app

from ..extensions import db

QUERY = """
    SELECT
    email,
    TRIM(CONCAT(first_name, ' ', last_name)) as "name"
    FROM creator
    WHERE is_deleted = false
    AND created > current_date - 1
"""


def update():
    nl_url = current_app.config.get("NEWSLETTER_URL")
    nl_list_id = current_app.config.get("NEWSLETTER_LIST_ID")
    nl_api_key = current_app.config.get("NEWSLETTER_API_KEY")
    creators = db.session.execute(QUERY).mappings().all()

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
