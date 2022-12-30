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

    pois = db.relationship("POI", back_populates="creator")
    images = db.relationship("Image", back_populates="creator")
    comments = db.relationship("Comment", back_populates="creator")

    def __repr__(self):
        return f'<Creator "{self.id}">'


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    created = db.Column(db.TIMESTAMP)
    modified = db.Column(
        db.TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )

    name = db.Column(db.String(255), nullable=False)
    is_published = db.Column(db.Boolean)

    pois = db.relationship("POI", back_populates="category")

    def __repr__(self):
        return f'<Category "{self.id}">'


class POI(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    created = db.Column(db.TIMESTAMP)
    modified = db.Column(
        db.TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )

    display_count = db.Column(db.Integer, nullable=False)
    position = db.Column(Geometry("POINT", srid=4326))
    is_published = db.Column(db.Boolean)

    creator_id = db.Column(db.Integer, db.ForeignKey("creator.id"))
    creator = db.relationship("Creator", back_populates="pois")

    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))
    category = db.relationship("Category", back_populates="pois")

    images = db.relationship("Image", back_populates="poi")
    comments = db.relationship("Comment", back_populates="poi")

    def __repr__(self):
        return f'<Image "{self.id}">'


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    created = db.Column(db.TIMESTAMP)
    modified = db.Column(
        db.TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )

    image_url = db.Column(db.String(2048))
    is_published = db.Column(db.Boolean)

    creator_id = db.Column(db.Integer, db.ForeignKey("creator.id"))
    creator = db.relationship("Creator", back_populates="images")

    poi_id = db.Column(db.Integer, db.ForeignKey("poi.id"))
    poi = db.relationship("POI", back_populates="images")

    def __repr__(self):
        return f'<Image "{self.id}">'


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    created = db.Column(db.TIMESTAMP)
    modified = db.Column(
        db.TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )

    text = db.Column(db.String(2048))
    is_published = db.Column(db.Boolean)

    creator_id = db.Column(db.Integer, db.ForeignKey("creator.id"))
    creator = db.relationship("Creator", back_populates="comments")

    poi_id = db.Column(db.Integer, db.ForeignKey("poi.id"))
    poi = db.relationship("POI", back_populates="comments")

    def __repr__(self):
        return f'<Comment "{self.id}">'
