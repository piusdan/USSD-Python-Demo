#!/usr/bin/env bash

celery worker -A app.worker.celery --loglevel=INFO