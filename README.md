# Na-ovoce.cz stats dashboard

## Prerequisites

* Python 3.11
* SQLite, Spatialite and SpatiaLite tools
* Nodejs

## Development
    # prepare and activate virtual environment
    python3 -m venv venv
    source venv/bin/activate

    # install backend dependencies
    pip install -r requirements-dev.txt

    # prepare (+edit) and load env variables
    cp .env.dev .env

    # populate database
    flask core init-db
    flask auth create-user someuser@example.com somepassword

    # load geo boundaries
    spatialite_tool -i -shp dashboard/resources/gis/cz_0 -d instance/dashboard.sqlite3 -t cz_0 -c utf-8 -s 4326
    spatialite_tool -i -shp dashboard/resources/gis/cz_1 -d instance/dashboard.sqlite3 -t cz_1 -c utf-8 -s 4326
    spatialite_tool -i -shp dashboard/resources/gis/cz_2 -d instance/dashboard.sqlite3 -t cz_2 -c utf-8 -s 4326

    # Add spatial indexes to the boundaries
    spatialite instance/dashboard.sqlite3
    spatialite> SELECT CreateSpatialIndex('cz_0', 'geometry');
    spatialite> SELECT CreateSpatialIndex('cz_1', 'geometry');
    spatialite> SELECT CreateSpatialIndex('cz_2', 'geometry');

    # install frontend dependencies
    npx yarn install

    # run development servers
    make dev
