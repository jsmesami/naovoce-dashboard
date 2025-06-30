import csv
import re
from datetime import datetime
from operator import attrgetter

from flask import current_app


def get_todays_exports(bucket, export_groups):
    def check_name(name):
        today = datetime.now().strftime("%Y-%m-%d")
        re_group = rf"({'|'.join(export_groups)})"
        re_today = rf"{today}_\d{{2}}-\d{{2}}-\d{{2}}"
        if match := re.match(rf"9288_{re_group}-{re_today}.csv", name):
            return match.group(1), match.group(0)

    # List bucket and return only last report groups it their name checks
    return dict(
        filter(
            None,
            (
                check_name(obj.key)
                for obj in sorted(
                    bucket.objects.all(),
                    key=attrgetter("last_modified"),
                    reverse=True,
                )[: len(export_groups)]
            ),
        )
    )


def download_export(bucket, dl_path, filename):
    current_app.logger.info(f"Downloading export {filename}")
    downloaded = dl_path / filename
    bucket.download_file(filename, downloaded)

    return downloaded


def read_export_data(export, adapter):
    current_app.logger.info(f"Reading export {export.name}")
    with export.open() as input_file:
        reader = csv.DictReader(input_file, delimiter=";")
        return {row["id"]: row for row in map(adapter, reader)}


def delete_export(export):
    current_app.logger.info(f"Deleting export {export.name}")
    export.unlink()
