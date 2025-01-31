#!/bin/bash

# Start the FastAPI server in the background
echo "Starting FastAPI server..."
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
SERVER_PID=$!

# Wait for server to start
echo "Waiting for server to start..."
sleep 5

# Generate and extract token
echo "Generating test token..."
TOKEN=$(python3 tests/generate_test_ws_token.py | grep "Test token:" | cut -d' ' -f3)

# Export token for test client
export TEST_TOKEN="$TOKEN"

# Run the WebSocket test
echo "Running WebSocket test..."
python3 tests/test_websocket_client.py

# Cleanup: Kill the server
kill $SERVER_PID

# Wait for server to shutdown
sleep 2
