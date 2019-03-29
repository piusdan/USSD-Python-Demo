#!/usr/bin/env bash

LOGLEVEL=info
NAME=nerds-microfinance-app
NUM_WORKERS=3
HOST=127.0.0.1
TIMEOUT=120
PORT=8000

echo "Starting $NAME"

# update db
flask initdb

exec gunicorn manage:app -b $HOST:$PORT \
    -w $NUM_WORKERS \
    -t $TIMEOUT \
    --log-level $LOGLEVEL
