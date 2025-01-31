#!/bin/bash
# Generate token and run WebSocket test

# Generate token and extract it
TOKEN=$(python3 generate_test_ws_token.py | grep "Test token:" | cut -d' ' -f3)

# Export token for test client
export TEST_TOKEN="$TOKEN"

# Run the test client with the token
python3 test_websocket_client.py
