import logging

from flask import current_app
from sqlalchemy import text

from ..extensions import db
from ..utils.commands import report_exception
from . import core, importer, maintenance, newsletter


@core.cli.command("init-db")
def init_db():
    """Initializes database with schema and SpatiaLite metadata."""
    db.session.execute(text("SELECT InitSpatialMetaData(1)"))
    db.create_all()
    db.session.commit()
    db.session.close()


@core.cli.command("update-db")
@report_exception(current_app)
def update_db():
    """Imports new data from Mapotic, executed daily with Cron"""
    current_app.logger.setLevel(logging.INFO)
    importer.update_db(db)


@core.cli.command("dump-emails")
def dump_emails():
    """Dumps emails to stdout as CSV to be imported to Sendy"""
    newsletter.dump_emails()


@core.cli.command("update-newsletter")
@report_exception(current_app)
def update_newsletter():
    """Subscribes new users to Sendy, executed daily with Cron"""
    current_app.logger.setLevel(logging.INFO)
    newsletter.update()


@core.cli.command("purge-exports")
@report_exception(current_app)
def purge_exports():
    """Purges old exports from the S3 bucket, executed daily with Cron"""
    current_app.logger.setLevel(logging.INFO)
    maintenance.purge_old_exports(current_app)
