import logging

from flask import current_app

from ..extensions import db
from . import core, importer, newsletter


@core.cli.command("init-db")
def init_db():
    db.create_all()


@core.cli.command("update-db")
def update_db():
    current_app.logger.setLevel(logging.INFO)
    importer.update_db(db)


@core.cli.command("update-newsletter")
def update_newsletter():
    current_app.logger.setLevel(logging.INFO)
    newsletter.update()
