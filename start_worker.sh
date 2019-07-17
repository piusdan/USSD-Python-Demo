#!/usr/bin/env bash
export PYTHONPATH=/opt/apps/app
export C_FORCE_ROOT=true
exec /appenv/bin/celery worker -A worker.celery --loglevel=INFO