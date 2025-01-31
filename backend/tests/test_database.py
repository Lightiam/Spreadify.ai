import os
import sys
from pathlib import Path
import pytest
from pytest_asyncio import fixture

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

from app.database import init_db, get_db
from app.models.user import User
from sqlalchemy.orm import Session

@pytest.mark.asyncio
async def test_crud():
    """Test basic CRUD operations with SQLite database."""
    # Initialize database
    init_db()
    
    # Get database session
    db = next(get_db())
    
    try:
        # Create
        test_user = User(
            email="test@example.com",
            name="Test User",
            google_id="test123"
        )
        db.add(test_user)
        db.commit()
        assert test_user.id is not None, "User should have an ID after creation"
        
        # Read
        user = db.query(User).filter(User.email == "test@example.com").first()
        assert user is not None, "Should be able to read created user"
        assert user.email == "test@example.com", "Email should match"
        assert user.name == "Test User", "Name should match"
        
        # Update
        user.name = "Updated Test User"
        db.commit()
        updated_user = db.query(User).filter(User.email == "test@example.com").first()
        assert updated_user.name == "Updated Test User", "Name should be updated"
        
        # Delete
        db.delete(user)
        db.commit()
        deleted_user = db.query(User).filter(User.email == "test@example.com").first()
        assert deleted_user is None, "User should be deleted"
            
    finally:
        db.close()

def test_database_connection():
    """Test that we can connect to the database and create tables."""
    from sqlalchemy import text
    init_db()
    db = next(get_db())
    try:
        # Simple query to verify connection using SQLAlchemy text()
        result = db.execute(text("SELECT 1")).scalar()
        assert result == 1, "Database connection should be working"
    finally:
        db.close()
