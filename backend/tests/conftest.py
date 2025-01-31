import os
import sys
import pytest
from pathlib import Path
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

from app.database import Base
from app.models.user import User

# Load environment variables
load_dotenv()

# Set up test database path and logging
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Use in-memory SQLite for tests
TEST_DB_URL = "sqlite:///:memory:"
logger.info(f"Using in-memory test database: {TEST_DB_URL}")

# Override environment variables for testing
os.environ["TEST_ENV"] = "1"
os.environ["DATABASE_URL"] = TEST_DB_URL
os.environ["LOG_LEVEL"] = "debug"

logger.info("Test environment variables set")

# Create test engine with proper SQLite settings
try:
    engine = create_engine(
        TEST_DB_URL,
        connect_args={
            "check_same_thread": False,
        },
        echo=True,  # Enable SQL logging for debugging
        pool_pre_ping=True,  # Enable connection health checks
        poolclass=StaticPool  # Use static pool for in-memory SQLite
    )
    logger.info("Test database engine created successfully")
except Exception as e:
    logger.error(f"Failed to create test database engine: {e}")
    raise

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # Prevent detached instance errors
)

@pytest.fixture(scope="function", autouse=True)
def setup_test_database():
    """Set up fresh test database for each test."""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Test database tables created")
        
        # Verify tables were created
        inspector = inspect(engine)
        expected_tables = {table.__tablename__ for table in Base.__subclasses__()}
        actual_tables = set(inspector.get_table_names())
        missing_tables = expected_tables - actual_tables
        if missing_tables:
            raise SQLAlchemyError(f"Failed to create tables: {missing_tables}")
        logger.info(f"Verified tables: {actual_tables}")
        
        # Test database connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            assert result == 1, "Database connection test failed"
            logger.info("Database connection verified")
        
        yield
    except Exception as e:
        logger.error(f"Test database setup failed: {e}")
        raise
    finally:
        # Clean up after test
        Base.metadata.drop_all(bind=engine)
        logger.info("Test database cleaned up")

@pytest.fixture
def db():
    """Get database session for testing with transaction rollback."""
    # Connect and begin a transaction
    connection = engine.connect()
    transaction = connection.begin()
    
    # Create session bound to this connection
    session = TestingSessionLocal(bind=connection)
    
    try:
        yield session
    finally:
        # Always rollback the transaction and close connections
        session.close()
        transaction.rollback()
        connection.close()

@pytest.fixture
def test_user():
    """Create a test user for authentication tests."""
    return {
        "email": "test@example.com",
        "name": "Test User",
        "google_id": "test123",
        "picture": "https://example.com/pic.jpg"
    }
