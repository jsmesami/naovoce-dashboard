import click
from flask import current_app
from werkzeug.security import generate_password_hash

from ..extensions import db
from ..utils.commands import wrap_command
from . import auth
from .models import User


@auth.cli.command("create-user")
@click.argument("email")
@click.argument("password")
@wrap_command(current_app)
def create_user(email, password):
    user = User(email=email, password=generate_password_hash(password, method="sha256"))
    db.session.add(user)
    db.session.commit()
