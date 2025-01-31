import os
import sys
from pathlib import Path
from sqlalchemy import text

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

from app.database import engine

def check_environment():
    """Check database and environment setup."""
    try:
        # Test database connection using raw engine connection
        with engine.connect() as connection:
            # Test basic connectivity
            result = connection.execute(text("SELECT 1")).scalar()
            assert result == 1, "Database connection test failed"
            print("Database connection verified")
            
            # Test table access
            tables = connection.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )).scalars().all()
            print(f"Available tables: {', '.join(tables)}")
            
            if 'users' in tables:
                # Test users table if it exists
                result = connection.execute(text("SELECT COUNT(*) FROM users")).scalar()
                print(f"Users table exists with {result} records")
            
        print("Environment check completed successfully")
        return True
    except Exception as e:
        print(f"Environment check failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = check_environment()
    sys.exit(0 if success else 1)
