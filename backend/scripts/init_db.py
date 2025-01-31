import logging
from sqlalchemy import text
from app.database import engine, Base, SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_database():
    """Initialize database with proper error handling and transaction management."""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Test database connection without transaction
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            assert result == 1, "Database connection test failed"
            logger.info("Database connection test passed")
            
        logger.info("Database initialization completed successfully")
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

if __name__ == "__main__":
    success = initialize_database()
    import sys
    sys.exit(0 if success else 1)
