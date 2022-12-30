from ..extensions import db
from . import core


@core.cli.command("init-db")
def init_db():
    db.create_all()
