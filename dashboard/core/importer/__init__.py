from pathlib import Path

from flask import current_app

from .adapters.database import ADAPTERS as DB_ADAPTERS
from .adapters.exports import ADAPTERS as EXPORT_ADAPTERS
from .database import db_delete, db_insert, db_update, read_db_data
from .exports import (
    delete_export,
    download_export,
    get_bucket,
    get_todays_exports,
    read_export_data,
)
from .mappings import EXPORT_GROUP_MODELS, EXPORT_GROUP_QUERIES, EXPORT_GROUPS


def update_db(db):
    bucket = get_bucket()
    todays_exports = get_todays_exports(bucket, EXPORT_GROUPS)

    current_app.logger.info("Running importer")

    if len(todays_exports) != len(EXPORT_GROUPS):
        current_app.logger.warning("Aborting: missing or incomplete exports")
        return

    dl_path = Path("~/.local/tmp/").expanduser()
    if not dl_path.exists():
        dl_path.mkdir(parents=True)

    for group in EXPORT_GROUPS:
        export = download_export(bucket, dl_path, todays_exports[group])
        export_rows = read_export_data(export, EXPORT_ADAPTERS[group])
        db_rows = read_db_data(db, EXPORT_GROUP_QUERIES[group], DB_ADAPTERS[group])

        model = EXPORT_GROUP_MODELS[group]
        current_app.logger.info(f"Syncing table {model.__table__}")
        db_delete(db, model, export_rows, db_rows)
        db_update(db, model, export_rows, db_rows)
        db_insert(db, model, export_rows, db_rows)

        delete_export(export)
