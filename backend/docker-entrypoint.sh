#!/bin/bash
set -e

echo "Starting Docker entrypoint script..."

# Function to handle errors
handle_error() {
    echo "Error occurred in entrypoint script: $1"
    exit 1
}

# Create and set permissions for data directory
echo "Setting up data directory..."
mkdir -p /app/data || handle_error "Failed to create data directory"
touch /app/data/app.db || handle_error "Failed to create database file"

# Set proper permissions
echo "Setting permissions..."
chown -R nobody:nogroup /app/data /app/data/app.db || handle_error "Failed to set ownership"
chmod 755 /app/data || handle_error "Failed to set directory permissions"
chmod 644 /app/data/app.db || handle_error "Failed to set database file permissions"

# Run database operations
echo "Running database operations..."
cd /app

# Initialize database
python3 scripts/init_db.py || handle_error "Database initialization failed"

# Run environment check
python3 scripts/check_environment.py || handle_error "Environment check failed"

# Run database migrations
alembic upgrade head || handle_error "Database migrations failed"

echo "Database initialization completed successfully"

# Start application
echo "Starting application..."
exec $*
