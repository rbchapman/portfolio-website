#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -e

echo "Starting backend build process..."

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install Python requirements
echo "Installing Python requirements..."
pip install -r requirements.txt

# Collect Django static files
echo "Collecting Django static files..."
python manage.py collectstatic --noinput

# Migrate Django database
echo "Running database migrations..."
python manage.py migrate

echo "Backend build process completed successfully!"