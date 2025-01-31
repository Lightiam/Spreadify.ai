import jwt  # Using PyJWT instead of python-jose
from datetime import datetime, timedelta
import os
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def generate_test_token():
    """Generate a test JWT token for WebSocket testing."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        # Use the same secret key as the main application
        secret_key = os.getenv("JWT_SECRET", "dev_jwt_secret_key_replace_in_production")
        if not secret_key:
            logger.error("JWT_SECRET not found in environment, using default")
        
        logger.info("Generating test token...")
        
        payload = {
            'sub': 'test@example.com',
            'exp': datetime.utcnow() + timedelta(minutes=30),
            'iat': datetime.utcnow(),
            'type': 'websocket'
        }
        
        token = jwt.encode(
            payload,
            secret_key,
            algorithm='HS256'
        )
        logger.info("Token generated successfully")
        print(f'Test token: {token}')
        return token
        
    except Exception as e:
        logger.error(f"Failed to generate token: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        generate_test_token()
    except Exception as e:
        logger.error(f"Token generation failed: {str(e)}")
        exit(1)
