#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Create migrations for any new models (no-op if no changes)
echo "Checking for new migrations..."
python manage.py makemigrations --noinput || echo "No new migrations to create"

# Run database migrations - this MUST succeed for deployment
echo "Applying database migrations..."
python manage.py migrate --noinput
echo "Migrations applied successfully!"

# Collect static files (clear existing first to avoid duplicate warnings)
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear
echo "Build completed successfully!"