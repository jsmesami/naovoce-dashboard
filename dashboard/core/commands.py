from ..extensions import db
from . import core, importer


@core.cli.command("update-db")
def update_db():
    importer.update_db(db)


@core.cli.command("init-db")
def init_db():
    db.create_all()
