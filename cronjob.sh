#!/usr/bin/env sh

source .env
venv/bin/flask core update-db 2>&1 | logger -t naovoce-update-db
venv/bin/flask core update-newsletter 2>&1 | logger -t naovoce-update-newsletter
