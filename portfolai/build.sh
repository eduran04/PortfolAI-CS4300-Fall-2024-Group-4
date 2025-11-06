#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Create migrations for any new models (no-op if no changes)
python manage.py makemigrations --noinput || echo "No new migrations to create"

# Run database migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput