import click
from werkzeug.security import generate_password_hash

from ..extensions import db
from . import auth
from .models import User


@auth.cli.command("create-user")
@click.argument("email")
@click.argument("password")
def create_user(email, password):
    db.session.add(
        User(email=email, password=generate_password_hash(password, method="scrypt"))
    )
    db.session.commit()
