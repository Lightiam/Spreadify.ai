import os
import sys
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

from app.database import init_db, get_db
from app.models.user import User

def test_environment():
    """Test the database environment setup."""
    try:
        # Set test environment
        os.environ["TEST_ENV"] = "1"
        logger.info("Test environment set")
        
        # Initialize database
        logger.info("Initializing database...")
        init_db()
        
        # Test database connection
        logger.info("Testing database connection...")
        db = next(get_db())
        try:
            # Create test user
            test_user = User(
                email="test@example.com",
                name="Test User"
            )
            db.add(test_user)
            db.commit()
            logger.info("Test user created successfully")
            
            # Query test user
            user = db.query(User).filter(User.email == "test@example.com").first()
            assert user is not None, "User should exist"
            logger.info("Test user queried successfully")
            
            # Cleanup
            db.delete(user)
            db.commit()
            logger.info("Test cleanup completed")
            
            return True
        finally:
            db.close()
            logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Environment test failed: {e}")
        raise

if __name__ == "__main__":
    success = test_environment()
    sys.exit(0 if success else 1)
