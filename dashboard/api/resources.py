from flask_restful import Resource
from sqlalchemy import text

from ..extensions import db


class TopUsers(Resource):
    def get(self):
        query = """
            WITH filtered_poi AS (
              SELECT creator_id
              FROM poi
              WHERE created >= now() - interval '30 day'
                AND is_deleted = false
                AND is_published = true
            )
            SELECT
              creator.id,
              TRIM(CONCAT(creator.first_name, ' ', creator.last_name)) as "name",
              (
                SELECT COUNT(*)
                FROM filtered_poi
                WHERE filtered_poi.creator_id = creator.id
              ) AS poi_count
            FROM creator
            WHERE (
              creator.is_deleted = false
              AND EXISTS(
                SELECT 1
                FROM filtered_poi
                WHERE filtered_poi.creator_id = creator.id
              )
            )
            ORDER BY poi_count DESC, "name"
            LIMIT 3
        """

        return [dict(row) for row in db.session.execute(text(query)).mappings().all()]
