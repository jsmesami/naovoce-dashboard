from collections import deque
from datetime import datetime, timedelta, timezone

from dashboard.core.s3 import get_bucket

OBJECT_KEEP_COUNT = 10
OBJECT_RETENTION_DAYS = 30


def purge_old_exports(current_app):
    current_app.logger.info("Running S3 purge")

    bucket = get_bucket(current_app)

    threshold_date = datetime.now(timezone.utc) - timedelta(days=OBJECT_RETENTION_DAYS)

    # Deque to keep only the N newest seen so far
    newest = deque(maxlen=OBJECT_KEEP_COUNT)
    to_delete = []

    for obj in sorted(
        bucket.objects.all(), key=lambda o: o.last_modified, reverse=True
    ):
        if len(newest) < OBJECT_KEEP_COUNT:
            newest.append(obj)
        elif obj.last_modified < threshold_date:
            to_delete.append(obj)

    if not to_delete:
        current_app.logger.info("No exports found to purge")
        return

    current_app.logger.info(f"Purging {len(to_delete)} exports from S3")
    for obj in to_delete:
        obj.delete()
