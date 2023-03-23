from datetime import datetime

from flask import current_app
from flask_sqlalchemy.session import Session
from sqlalchemy import text


def mark_modified(row):
    row["modified"] = datetime.now()
    return row


def mark_deleted(row, val):
    row["is_deleted"] = val
    return row


def db_delete(db, model, export_rows, db_rows):
    ids_to_delete = set(db_rows.keys()) - set(export_rows.keys())

    mappings_to_update = [
        mark_deleted(mark_modified(db_rows[id_]), True) for id_ in ids_to_delete
    ]

    if ids_to_delete:
        current_app.logger.info(
            "Removing {count} rows from table {table}".format(
                count=len(ids_to_delete), table=model.__table__
            )
        )
        session = Session(db)
        with session.begin():
            session.bulk_update_mappings(model, mappings_to_update)


def db_update(db, model, export_rows, db_rows):
    ids_to_update = set(export_rows.keys()) & set(db_rows.keys())

    mappings_to_update = [
        mark_deleted(mark_modified(export_rows[id_]), False)
        for id_ in ids_to_update
        if export_rows[id_] != db_rows[id_]
    ]

    if mappings_to_update:
        current_app.logger.info(
            "Updating {count} rows in table {table}".format(
                count=len(mappings_to_update), table=model.__table__
            )
        )
        session = Session(db)
        with session.begin():
            session.bulk_update_mappings(model, mappings_to_update)


def db_insert(db, model, export_rows, db_rows):
    ids_to_insert = set(export_rows.keys()) - set(db_rows.keys())

    mappings_to_insert = [
        mark_deleted(export_rows[id_], False) for id_ in ids_to_insert
    ]

    if mappings_to_insert:
        current_app.logger.info(
            "Inserting {count} rows to table {table}".format(
                count=len(mappings_to_insert), table=model.__table__
            )
        )
        session = Session(db)
        with session.begin():
            session.bulk_insert_mappings(model, mappings_to_insert)


def read_db_data(db, query, adapter):
    return {
        row["id"]: row
        for row in map(
            adapter, map(dict, db.session.execute(text(query)).mappings().all())
        )
    }
