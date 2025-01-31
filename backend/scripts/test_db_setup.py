import os
import sys
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

from app.database import init_db, get_db
from app.models.user import User

def test_database_setup():
    """Test database setup and basic operations."""
    try:
        # Set test environment
        os.environ["TEST_ENV"] = "1"
        os.environ["DATABASE_URL"] = "sqlite:////home/ubuntu/.spreadify/test/test.db"
        
        # Create test directory
        test_dir = Path("/home/ubuntu/.spreadify/test")
        test_dir.mkdir(parents=True, exist_ok=True)
        os.chmod(test_dir, 0o755)
        
        logger.info("Initializing database...")
        init_db()
        
        # Test database connection
        logger.info("Testing database connection...")
        db = next(get_db())
        try:
            # Create test user
            test_user = User(
                email="test@example.com",
                name="Test User",
                google_id="test123"
            )
            db.add(test_user)
            db.commit()
            logger.info("Successfully created test user")
            
            # Query test user
            user = db.query(User).filter(User.email == "test@example.com").first()
            assert user is not None, "User should exist"
            assert user.email == "test@example.com", "Email should match"
            logger.info("Successfully queried test user")
            
            return True
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Database test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_database_setup()
    sys.exit(0 if success else 1)
