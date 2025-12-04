#!/bin/sh
set -e  # Exit on any error

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Applying database migrations..."
python manage.py migrate

echo "Starting Gunicorn..."
exec gunicorn quizstrike.wsgi:application --bind 0.0.0.0:8002 --workers 3
