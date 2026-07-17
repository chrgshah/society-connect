#!/bin/sh
set -e

python manage.py migrate --noinput
python manage.py loaddata 2_categories --verbosity 1

exec gunicorn \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-2}" \
    --timeout "${GUNICORN_TIMEOUT:-60}" \
    society_connect.wsgi:application
