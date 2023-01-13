# Na-ovoce.cz stats dashboard

## Prerequisites

* Python 3.11
* Postgres
* Node.js
* Yarn

## Development

    # prepare database
    psql -U postgres postgres -c "CREATE ROLE naovoce SUPERUSER"
    psql -U postgres postgres -c "ALTER ROLE naovoce LOGIN"
    psql -U postgres postgres -c "CREATE DATABASE naovoce_dashboard OWNER=naovoce"
    psql -U naovoce naovoce_dashboard -c "CREATE EXTENSION postgis"

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

    # install frontend dependencies
    yarn

    # run development servers
    honcho start
