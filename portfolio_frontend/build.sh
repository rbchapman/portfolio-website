#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -e

echo "Starting frontend build process..."

# Install frontend dependencies
echo "Installing frontend dependencies..."
npm install

# Build frontend
echo "Building frontend..."
npm run build

echo "Frontend build process completed successfully!"