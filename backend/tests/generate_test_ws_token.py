import jwt
from datetime import datetime, timedelta
import os

def generate_test_token():
    """Generate a test JWT token for WebSocket testing."""
    from dotenv import load_dotenv
    load_dotenv()
    
    # Use the same secret key as the main application
    secret_key = os.getenv("JWT_SECRET", "dev_jwt_secret_key_replace_in_production")
    token = jwt.encode(
        {
            'sub': 'test@example.com',
            'exp': datetime.utcnow() + timedelta(minutes=30)
        },
        secret_key,
        algorithm='HS256'
    )
    print(f'Test token: {token}')

if __name__ == "__main__":
    generate_test_token()
