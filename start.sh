#!/bin/bash
set -e

echo "======================================"
echo "Starting Jetpo deployment..."
echo "======================================"

echo "Running database migrations..."
python manage.py migrate --noinput

echo "======================================"
echo "Migrations complete!"
echo "Starting Gunicorn server..."
echo "======================================"

exec gunicorn config.wsgi --log-file - --log-level info --bind 0.0.0.0:$PORT
