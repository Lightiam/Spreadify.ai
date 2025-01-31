from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

import pathlib

# Set up database paths
DB_DIR = pathlib.Path("/app/data")
DB_FILE = DB_DIR / "app.db"

# Get database URL from environment or use SQLite as fallback
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_FILE}")

# Handle PostgreSQL URL format for SQLAlchemy
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Configure SQLite for better concurrency and set pragmas for better performance
connect_args = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False,
    }

print(f"Using database URL: {SQLALCHEMY_DATABASE_URL}")
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    """Initialize the database, creating all tables."""
    import os
    
    # Ensure the data directory exists with proper permissions
    data_dir = "/app/data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
        # Ensure the directory is writable by the nobody user
        os.chmod(data_dir, 0o777)
    
    # Initialize database
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency for getting database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
