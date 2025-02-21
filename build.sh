#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -e

echo "Starting build process..."

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

# Move to frontend directory
echo "Changing to frontend directory..."
cd portfolio_frontend

# Install frontend dependencies
echo "Installing frontend dependencies..."
npm install

# Build frontend
echo "Building frontend..."
npm run build

echo "Build process completed successfully!"