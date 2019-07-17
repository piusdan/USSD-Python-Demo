#!/usr/bin/env bash

export LC_ALL=C.UTF-8
export LANG=C.UTF-8
export FLASK_APP=manage.py

/appenv/bin/flask initdb

exec /appenv/bin/flask run --host 0.0.0.0 --port 8000
