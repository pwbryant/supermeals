#!/bin/sh
python manage.py collectstatic --noinput
gunicorn supermeals.wsgi:application --bind 0.0.0.0:8000 --reload

