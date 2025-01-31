#!/bin/bash
set -e

echo "=== Setting up test environment ==="

# Set up environment variables
export PYTHONPATH=/home/ubuntu/spreadify/backend
export TEST_ENV=1
export DATABASE_URL="sqlite:///$(pwd)/test.db"
export LOG_LEVEL="debug"

# Create test directories with proper permissions
mkdir -p ~/.spreadify/test
chmod 755 ~/.spreadify/test

echo "=== Running database tests ==="

# Run the test environment check first
echo "Running environment check..."
python3 scripts/test_environment.py

# Run the database tests
echo "Running database tests..."
python3 -m pytest tests/test_database.py -v

echo "=== Tests completed ==="
