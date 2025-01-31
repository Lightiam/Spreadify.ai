import os
import sys
from pathlib import Path
import pytest
import logging
from sqlalchemy import text, inspect
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

from app.database import init_db, get_db
from app.models.user import User

# Set up logging
logger = logging.getLogger(__name__)

def test_crud(db: Session):
    """Test basic CRUD operations with SQLite database."""
    logger.info("Starting CRUD test...")
    
    # Create test user
    test_user = User(
        email="test@example.com",
        name="Test User",
        google_id="test123"
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)  # Refresh to ensure we have the latest data
    logger.info("Test user created successfully")
    
    # Verify user was created
    assert test_user.id is not None, "User should have an ID after creation"
    logger.info(f"User created with ID: {test_user.id}")
    
    # Read test
    user = db.query(User).filter(User.email == "test@example.com").first()
    assert user is not None, "Should be able to read created user"
    assert user.email == "test@example.com", "Email should match"
    assert user.name == "Test User", "Name should match"
    logger.info("User read test passed")
    
    # Update test
    user.name = "Updated Test User"
    db.commit()
    db.refresh(user)  # Refresh to ensure we have the latest data
    updated_user = db.query(User).filter(User.email == "test@example.com").first()
    assert updated_user.name == "Updated Test User", "Name should be updated"
    logger.info("User update test passed")
    
    # Delete test
    db.delete(user)
    db.commit()
    deleted_user = db.query(User).filter(User.email == "test@example.com").first()
    assert deleted_user is None, "User should be deleted"
    logger.info("User delete test passed")
            
    # No need for cleanup - transaction will be rolled back by fixture

def test_database_connection(db: Session):
    """Test database connection and basic operations."""
    # Test database connection
    logger.info("Testing database connection...")
    result = db.execute(text("SELECT 1")).scalar()
    assert result == 1, "Database connection should be working"
    logger.info("Database connection test successful")
    
    # Test table creation and basic operations
    logger.info("Testing table creation and operations...")
    test_user = User(
        email="test@example.com",
        name="Test User",
        google_id="test123"
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)  # Refresh to ensure we have the latest data
    logger.info("Test user created successfully")
    
    # Verify user creation
    user = db.query(User).filter(User.email == "test@example.com").first()
    assert user is not None, "Should be able to retrieve created user"
    assert user.email == "test@example.com", "Email should match"
    assert user.name == "Test User", "Name should match"
    logger.info("User creation verified successfully")
    
    # No need for cleanup - transaction will be rolled back by fixture
    logger.info("Test completed")
