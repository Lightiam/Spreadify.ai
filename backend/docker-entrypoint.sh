#!/bin/bash
set -e

# Create and set permissions for data directory
mkdir -p /app/data
touch /app/data/app.db
chown -R nobody:nogroup /app/data /app/data/app.db
chmod 777 /app/data
chmod 666 /app/data/app.db

# Initialize database configuration
python3 /app/scripts/configure_alembic.py

# Switch to nobody user and run migrations
su nobody -s /bin/bash -c "alembic upgrade head"

# Start application with a single worker
exec su nobody -s /bin/bash -c "uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1"
