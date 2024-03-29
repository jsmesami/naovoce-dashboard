import logging

from flask import current_app
from sqlalchemy import text

from ..extensions import db
from ..utils.commands import wrap_command
from . import core, importer, newsletter


@core.cli.command("init-db")
@wrap_command(current_app)
def init_db():
    """Initializes database with schema.
    Remember to `GRANT rds_superuser TO naovoce;` on AWS RDS
    """
    db.create_all()
    db.session.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
    db.session.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
    db.session.execute(
        text(
            """
                CREATE INDEX IF NOT EXISTS users_fti
                ON creator
                USING gin(email gin_trgm_ops, first_name gin_trgm_ops, last_name gin_trgm_ops);
            """
        )
    )
    db.session.commit()


@core.cli.command("update-db")
@wrap_command(current_app)
def update_db():
    """Imports new data from Mapotic, executed daily with Cron"""
    current_app.logger.setLevel(logging.INFO)
    importer.update_db(db)


@core.cli.command("dump-emails")
@wrap_command(current_app)
def dump_emails():
    """Dumps emails to stdout as CSV to be imported to Sendy"""
    newsletter.dump_emails()


@core.cli.command("update-newsletter")
@wrap_command(current_app)
def update_newsletter():
    """Subscribes new users to Sendy, executed daily with Cron"""
    current_app.logger.setLevel(logging.INFO)
    newsletter.update()
