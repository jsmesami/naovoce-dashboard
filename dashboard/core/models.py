from geoalchemy2 import Geometry
from sqlalchemy.sql import func

from ..extensions import db


class Creator(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    created = db.Column(db.TIMESTAMP)
    modified = db.Column(
        db.TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )

    first_name = db.Column(db.String(127))
    last_name = db.Column(db.String(127))
    email = db.Column(db.String(255))
    last_visit = db.Column(db.TIMESTAMP)

    def __repr__(self):
        return f'<Creator "{self.id}">'


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    created = db.Column(db.TIMESTAMP)
    modified = db.Column(
        db.TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )

    name = db.Column(db.String(255))
    is_published = db.Column(db.Boolean)

    def __repr__(self):
        return f'<Category "{self.id}">'


class POI(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    created = db.Column(db.TIMESTAMP)
    modified = db.Column(
        db.TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )

    display_count = db.Column(db.Integer)
    position = db.Column(Geometry("POINT", srid=4326))
    is_published = db.Column(db.Boolean)

    creator_id = db.Column(db.Integer, index=True)
    category_id = db.Column(db.Integer, index=True)

    def __repr__(self):
        return f'<Image "{self.id}">'


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    created = db.Column(db.TIMESTAMP)
    modified = db.Column(
        db.TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )

    image_url = db.Column(db.String(1024 * 2))
    is_published = db.Column(db.Boolean)

    creator_id = db.Column(db.Integer, index=True)
    poi_id = db.Column(db.Integer, index=True)

    def __repr__(self):
        return f'<Image "{self.id}">'


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    created = db.Column(db.TIMESTAMP)
    modified = db.Column(
        db.TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )

    text = db.Column(db.String(1024 * 5))
    is_published = db.Column(db.Boolean)

    creator_id = db.Column(db.Integer, index=True)
    poi_id = db.Column(db.Integer, index=True)

    def __repr__(self):
        return f'<Comment "{self.id}">'
