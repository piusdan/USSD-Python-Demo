#!/usr/bin/env bash

exec appenv/bin/celery worker -A app.celery --loglevel=INFO