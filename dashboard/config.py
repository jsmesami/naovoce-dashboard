import ast
import os
from contextlib import suppress
from pathlib import Path


class ImproperlyConfigured(Exception):
    pass


def env(key, default=None):

    value = os.environ.get(key, default)

    with suppress(SyntaxError, ValueError):
        return ast.literal_eval(value)

    if value is None:
        raise ImproperlyConfigured(f"Missing required environment variable '{key}'.")

    return value


BASE_DIR = Path(__file__).parent.parent


class Config:
    SECRET_KEY = env("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = env("DATABASE_URI") or "sqlite:///" + str(
        BASE_DIR / "dashboard.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
