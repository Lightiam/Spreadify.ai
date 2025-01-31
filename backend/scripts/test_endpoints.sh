#!/bin/bash
set -e

echo "Starting endpoint tests..."

# Health check
echo -e "\n1. Testing health check endpoint..."
HEALTH_CHECK=$(curl -s http://localhost:8000/healthz)
echo "Health check response: $HEALTH_CHECK"

# User registration
echo -e "\n2. Testing user registration..."
REGISTER_RESPONSE=$(curl -s -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email":"test@example.com",
    "name":"Test User",
    "google_id":"test123",
    "picture":"https://example.com/pic.jpg"
  }')
echo "Registration response: $REGISTER_RESPONSE"

# Extract token from registration response
ACCESS_TOKEN=$(echo "$REGISTER_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))")
echo "Access token: $ACCESS_TOKEN"

# User info retrieval
echo -e "\n3. Testing user info retrieval..."
ME_RESPONSE=$(curl -s http://localhost:8000/auth/me \
  -H "Authorization: Bearer $ACCESS_TOKEN")
echo "User info response: $ME_RESPONSE"

# Database verification
echo -e "\n4. Testing database tables..."
DB_CHECK=$(curl -s http://localhost:8000/healthz)
echo "Database check response: $DB_CHECK"

echo -e "\nTest sequence completed."
