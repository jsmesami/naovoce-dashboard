from datetime import datetime

from flask_sqlalchemy.session import Session


def wrap_modified(row):
    row["modified"] = datetime.now()
    return row


def db_delete(db, model, export_rows, db_rows):
    ids_to_delete = set(db_rows.keys()) - set(export_rows.keys())

    if ids_to_delete:
        session = Session(db)
        statement = model.__table__.delete().where(model.id.in_(ids_to_delete))
        with session.begin():
            session.execute(statement)


def db_update(db, model, export_rows, db_rows):
    ids_to_update = set(export_rows.keys()) & set(db_rows.keys())

    mappings_to_update = [
        wrap_modified(export_rows[id_])
        for id_ in ids_to_update
        if export_rows[id_] != db_rows[id_]
    ]

    if mappings_to_update:
        session = Session(db)
        with session.begin():
            session.bulk_update_mappings(model, mappings_to_update)


def db_insert(db, model, export_rows, db_rows):
    ids_to_insert = set(export_rows.keys()) - set(db_rows.keys())

    mappings_to_insert = [export_rows[id_] for id_ in ids_to_insert]

    if mappings_to_insert:
        session = Session(db)
        with session.begin():
            session.bulk_insert_mappings(model, mappings_to_insert)


def read_db_data(db, query, adapter):
    session = Session(db)
    with session.begin():
        return {
            row["id"]: row
            for row in map(adapter, map(dict, session.execute(query).mappings().all()))
        }
