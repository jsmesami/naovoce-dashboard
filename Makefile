#!/usr/bin/env sh

reqs:
	pip-compile --resolver=backtracking --upgrade -o requirements.txt pyproject.toml
	pip-compile --resolver=backtracking --upgrade --extra dev -o requirements-dev.txt pyproject.toml

fmt:
	isort .
	black .

run:
	gunicorn -b :8888 dashboard.main:app

dev:
	flask --app dashboard.main --debug run
