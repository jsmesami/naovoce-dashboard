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
    SQLALCHEMY_DATABASE_URI = env("DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
    S3_BUCKET_NAME = env("S3_BUCKET_NAME")
    EMAIL_USER = env("EMAIL_USER")
    EMAIL_PASSWORD = env("EMAIL_PASSWORD")
    EMAIL_HOST = env("EMAIL_HOST")
    EMAIL_PORT = env("EMAIL_PORT")
    NEWSLETTER_URL = env("NEWSLETTER_URL")
    NEWSLETTER_API_KEY = env("NEWSLETTER_API_KEY")
    NEWSLETTER_LIST_ID = env("NEWSLETTER_LIST_ID")
