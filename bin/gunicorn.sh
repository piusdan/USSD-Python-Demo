#!/usr/bin/env bash

ls -lt

source appenv/bin/activate

python manage.py initdb

python manage.py runserver --host 0.0.0.0 --port 8000
