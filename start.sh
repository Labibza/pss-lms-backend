#!/bin/sh

set -e

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Creating or updating admin user..."
    python manage.py create_admin
fi

if [ "$RUN_SEED_DATA" = "True" ]; then
    echo "Running seed data..."
    python manage.py seed_data
fi

echo "Starting Gunicorn..."
gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000}