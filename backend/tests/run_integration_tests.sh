#!/bin/bash
set -e

echo "=== Setting up test environment ==="
# Ensure database directory exists with proper permissions
mkdir -p /home/ubuntu/.spreadify
chmod 755 /home/ubuntu/.spreadify

# Set up environment variables
export PYTHONPATH=/home/ubuntu/spreadify/backend:$PYTHONPATH
export DATABASE_URL="sqlite:////home/ubuntu/.spreadify/test.db"
export TEST_DATABASE_URL="sqlite:////home/ubuntu/.spreadify/test.db"
export JWT_SECRET="dev_jwt_secret_key_replace_in_production"
export LOG_LEVEL="debug"

# Initialize database
echo "Initializing database..."
python3 -c "from app.database import init_db; init_db()"

# Wait for database initialization
sleep 2

# Start the FastAPI server in the background with detailed logging
echo "Starting FastAPI server..."
PYTHONPATH=/home/ubuntu/spreadify/backend:$PYTHONPATH \
DATABASE_URL="sqlite:////home/ubuntu/.spreadify/test.db" \
JWT_SECRET="dev_jwt_secret_key_replace_in_production" \
LOG_LEVEL="debug" \
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level debug --reload > server.log 2>&1 &
SERVER_PID=$!

# Wait for server to start and verify it's running
echo "Waiting for server to start..."
max_attempts=30
attempt=0
while ! curl -s http://localhost:8000/healthz > /dev/null; do
    if [ $attempt -gt $max_attempts ]; then
        echo "Server failed to start. Check server.log for details."
        cat server.log
        kill $SERVER_PID 2>/dev/null || true
        exit 1
    fi
    echo "Attempt $attempt: Waiting for server to start..."
    sleep 1
    attempt=$((attempt + 1))
done

echo "Server started successfully."

# Generate test token with error handling
echo "Generating test token..."
TOKEN_OUTPUT=$(python3 tests/generate_test_ws_token.py)
if [ $? -ne 0 ]; then
    echo "Failed to generate token:"
    echo "$TOKEN_OUTPUT"
    kill $SERVER_PID 2>/dev/null || true
    exit 1
fi

export TEST_TOKEN=$(echo "$TOKEN_OUTPUT" | grep "Test token:" | cut -d' ' -f3)
if [ -z "$TEST_TOKEN" ]; then
    echo "Failed to extract token from output:"
    echo "$TOKEN_OUTPUT"
    kill $SERVER_PID 2>/dev/null || true
    exit 1
fi

echo "Test token generated successfully"

# Run WebSocket test with timeout and proper environment
echo "=== Running WebSocket Tests ==="
PYTHONPATH=/home/ubuntu/spreadify/backend:$PYTHONPATH \
DATABASE_URL="sqlite:////home/ubuntu/.spreadify/test.db" \
JWT_SECRET="dev_jwt_secret_key_replace_in_production" \
timeout 30s python3 tests/test_websocket_client.py
WS_TEST_RESULT=$?

# Check WebSocket test result
if [ $WS_TEST_RESULT -ne 0 ]; then
    echo "WebSocket test failed with exit code: $WS_TEST_RESULT"
    echo "Server logs:"
    cat server.log
fi

# Run database tests
echo "=== Running Database Tests ==="
python3 -m pytest tests/test_database.py -v
DB_TEST_RESULT=$?

# Cleanup
echo "=== Cleaning up ==="
kill $SERVER_PID 2>/dev/null || true
wait $SERVER_PID 2>/dev/null || true

echo "=== Test Results ==="
if [ -f server.log ]; then
    echo "Server Logs (last 50 lines):"
    tail -n 50 server.log
fi

# Exit with proper status
if [ $WS_TEST_RESULT -ne 0 ] || [ $DB_TEST_RESULT -ne 0 ]; then
    echo "Tests failed!"
    exit 1
fi

echo "All tests passed successfully!"
