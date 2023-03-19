from flask_login import UserMixin
from sqlalchemy.sql import func

from ..extensions import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.TIMESTAMP, server_default=func.now())
    modified = db.Column(
        db.TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

    zones = db.relationship("Zone", back_populates="author")

    def __repr__(self):
        return f'<User "{self.email}">'
