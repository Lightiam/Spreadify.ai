from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

import pathlib

# Set up database paths
DB_DIR = pathlib.Path("/app/data") if os.getenv("DOCKER_ENV") else pathlib.Path.home() / ".spreadify"
DB_FILE = DB_DIR / "app.db"

# Create directory if it doesn't exist
DB_DIR.mkdir(parents=True, exist_ok=True)

# Get database URL from environment or use SQLite as fallback
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
if not SQLALCHEMY_DATABASE_URL:
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_FILE}"

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
    if not DB_DIR.exists():
        DB_DIR.mkdir(parents=True, exist_ok=True)
        
    # Set appropriate permissions based on environment
    if os.getenv("DOCKER_ENV"):
        # In Docker, we're running as nobody user
        try:
            import pwd
            nobody_uid = pwd.getpwnam('nobody').pw_uid
            nobody_gid = pwd.getpwnam('nobody').pw_gid
            os.chown(DB_DIR, nobody_uid, nobody_gid)
            os.chmod(DB_DIR, 0o755)
            if DB_FILE.exists():
                os.chown(DB_FILE, nobody_uid, nobody_gid)
                os.chmod(DB_FILE, 0o644)
        except Exception as e:
            print(f"Warning: Could not set Docker permissions: {e}")
    else:
        # Local development
        os.chmod(DB_DIR, 0o755)
        if DB_FILE.exists():
            os.chmod(DB_FILE, 0o644)
    
    # Initialize database
    Base.metadata.create_all(bind=engine)
    print(f"Database initialized at {DB_FILE}")

def get_db():
    """Dependency for getting database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
