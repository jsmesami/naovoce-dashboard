#!/usr/bin/env sh

reqs:
	pip-compile --resolver=backtracking --upgrade -o requirements.txt pyproject.toml
	pip-compile --resolver=backtracking --upgrade --extra dev -o requirements-dev.txt pyproject.toml

fmt:
	isort .
	black .

compile-assets:
	yarn && yarn build

run:
	gunicorn -b :8888 dashboard:app

dev:
	honcho start
