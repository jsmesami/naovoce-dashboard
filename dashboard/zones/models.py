from geoalchemy2 import Geometry
from sqlalchemy.sql import func

from ..extensions import db


class Zone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    area = db.Column(Geometry("MULTIPOLYGON", srid=4326), nullable=False)

    author_id = db.mapped_column(db.ForeignKey("user.id", ondelete="SET NULL"))
    author = db.relationship("User", back_populates="zones")

    created = db.Column(db.TIMESTAMP, server_default=func.now())
    modified = db.Column(
        db.TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )

    def __repr__(self):
        return f'<Zone "{self.name}">'
