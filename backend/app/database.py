from sqlalchemy import create_engine, text, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import os
from dotenv import load_dotenv

load_dotenv()

import pathlib

# Set up logging
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set up database configuration based on environment
if os.getenv("TEST_ENV"):
    # Use in-memory SQLite for tests
    DB_DIR = None
    DB_FILE = None
    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
    logger.info("Using in-memory SQLite database for tests")
elif os.getenv("DOCKER_ENV"):
    DB_DIR = pathlib.Path("/app/data")
    DB_FILE = DB_DIR / "app.db"
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_FILE}"
    logger.info(f"Using Docker database: {DB_FILE}")
    
    try:
        DB_DIR.mkdir(parents=True, exist_ok=True)
        os.chmod(DB_DIR, 0o755)
        logger.info(f"Docker database directory created: {DB_DIR}")
    except Exception as e:
        logger.error(f"Failed to set up Docker database directory: {e}")
        raise
else:
    # Default to local development environment
    DB_DIR = pathlib.Path.home() / ".spreadify"
    DB_FILE = DB_DIR / "app.db"
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_FILE}")
    logger.info(f"Using local database: {DB_FILE}")
    
    if SQLALCHEMY_DATABASE_URL.startswith("sqlite:"):
        try:
            DB_DIR.mkdir(parents=True, exist_ok=True)
            os.chmod(DB_DIR, 0o755)
            logger.info(f"Local database directory created: {DB_DIR}")
            
            if DB_FILE.exists():
                os.chmod(DB_FILE, 0o644)
                logger.info("Database file permissions set")
        except Exception as e:
            logger.error(f"Failed to set up local database: {e}")
            raise

# Handle PostgreSQL URL format for SQLAlchemy
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Configure database engine based on URL type
connect_args = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite:"):
    connect_args["check_same_thread"] = False
    if SQLALCHEMY_DATABASE_URL == "sqlite:///:memory:":
        from sqlalchemy.pool import StaticPool
        engine = create_engine(
            SQLALCHEMY_DATABASE_URL,
            connect_args=connect_args,
            pool_pre_ping=True,
            poolclass=StaticPool,  # Use static pool for in-memory SQLite
            echo=True  # Enable SQL logging for debugging
        )
        logger.info("Using in-memory SQLite with StaticPool")
    else:
        engine = create_engine(
            SQLALCHEMY_DATABASE_URL,
            connect_args=connect_args,
            pool_pre_ping=True,
            echo=True  # Enable SQL logging for debugging
        )
        logger.info(f"Using SQLite database at {SQLALCHEMY_DATABASE_URL}")
else:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_pre_ping=True,
        echo=True  # Enable SQL logging for debugging
    )
    logger.info(f"Using database at {SQLALCHEMY_DATABASE_URL}")

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # Prevent detached instance errors
)
Base = declarative_base()

def init_db():
    """Initialize the database, creating all tables."""
    import os
    
    try:
        # Handle file-based SQLite database setup
        if DB_DIR and DB_FILE:  # Skip for in-memory database
            try:
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
                        logger.warning(f"Could not set Docker permissions: {e}")
                else:
                    # Local development
                    os.chmod(DB_DIR, 0o755)
                    if DB_FILE.exists():
                        os.chmod(DB_FILE, 0o644)
                
                logger.info(f"Database directory configured at {DB_DIR}")
            except Exception as e:
                logger.error(f"Failed to configure database directory: {e}")
                raise
        
        # Initialize database schema
        Base.metadata.create_all(bind=engine)
        logger.info("Database schema initialized successfully")
        
        # Test database connection and verify tables
        with engine.connect() as connection:
            # Test basic connectivity
            result = connection.execute(text("SELECT 1")).scalar()
            assert result == 1, "Database connection test failed"
            
            # Verify tables
            tables = connection.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )).scalars().all()
            
            # Check for required tables
            expected_tables = {table.__tablename__ for table in Base.__subclasses__()}
            actual_tables = set(tables)
            missing_tables = expected_tables - actual_tables
            
            if missing_tables:
                raise Exception(f"Failed to create tables: {missing_tables}")
            
            logger.info(f"Verified tables: {actual_tables}")
            logger.info("Database connection test successful")
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    
    logger.info("Database initialization completed successfully")

def get_db():
    """Dependency for getting database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
