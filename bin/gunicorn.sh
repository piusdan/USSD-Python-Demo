#!/usr/bin/env bash

LOGLEVEL=info
NAME=nerds-microfinance-app
NUM_WORKERS=3
HOST=0.0.0.0
TIMEOUT=120
PORT=8000

echo "Starting $NAME"

# update db
export FLASK_APP=manage.py
flask initdb

exec gunicorn manage:app -b $HOST:$PORT \
    -w $NUM_WORKERS \
    -t $TIMEOUT \
    --log-level $LOGLEVEL
