#!/usr/bin/env bash
source appenv/bin/activate

appenv/bin/celery worker -A app.worker.celery --loglevel=INFO