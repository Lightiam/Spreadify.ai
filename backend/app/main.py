from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
from app.database import init_db, get_db
from app.routers import auth, streams, stripe, webrtc
from sqlalchemy.orm import Session
from sqlalchemy import text

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Spreadify API",
    description="API for Spreadify streaming platform",
    version="1.0.0"
)

# Configure CORS
cors_origins = eval(os.getenv("CORS_ORIGINS", '["http://localhost:5173"]'))
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with database dependency
app.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth"],
    dependencies=[Depends(get_db)]
)
app.include_router(
    streams.router,
    prefix="/streams",
    tags=["streams"],
    dependencies=[Depends(get_db)]
)
app.include_router(
    stripe.router,
    prefix="/stripe",
    tags=["stripe"],
    dependencies=[Depends(get_db)]
)
app.include_router(
    webrtc.router,
    prefix="/webrtc",
    tags=["webrtc"],
    dependencies=[Depends(get_db)]
)

# Health check endpoint with database verification
@app.get("/healthz")
async def health_check(db: Session = Depends(get_db)):
    try:
        # Basic health check first
        basic_health = {
            "status": "healthy",
            "version": "1.0.0",
        }

        # Try to verify database connection
        try:
            db.execute(text("SELECT 1"))
            basic_health["database"] = "connected"
        except Exception as db_err:
            print(f"Database connection error: {str(db_err)}")
            basic_health["database"] = "error"
            basic_health["database_error"] = str(db_err)
            return basic_health

        # Try to verify CRUD operations
        try:
            from app.crud.user import create_user, get_user_by_email, update_user, delete_user
            from app.schemas.auth import UserCreate, UserUpdate
            
            # Create test user
            test_user = UserCreate(
                email="test@example.com",
                name="Test User",
                google_id="test123",
                picture="https://example.com/pic.jpg"
            )
            db_user = create_user(db, test_user)
            
            # Verify user was created
            found_user = get_user_by_email(db, "test@example.com")
            if not found_user:
                raise Exception("Failed to create and retrieve user")
                
            # Update user
            update_data = UserUpdate(name="Updated Test User")
            updated_user = update_user(db, found_user.id, update_data)
            if updated_user.name != "Updated Test User":
                raise Exception("Failed to update user")
                
            # Delete user
            deleted_user = delete_user(db, found_user.id)
            if not deleted_user:
                raise Exception("Failed to delete user")
                
            # Verify deletion
            deleted_check = get_user_by_email(db, "test@example.com")
            if deleted_check:
                raise Exception("User was not properly deleted")
            
            basic_health["crud_test"] = "passed"
        except Exception as crud_err:
            print(f"CRUD test error: {str(crud_err)}")
            basic_health["crud_test"] = "error"
            basic_health["crud_error"] = str(crud_err)
        
        return basic_health

    except Exception as e:
        print(f"Health check error: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "version": "1.0.0"
        }

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    try:
        init_db()
        print("Database tables created successfully")
        # Run migrations
        import subprocess
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        print("Database migrations completed successfully")
    except Exception as e:
        print(f"Error during database initialization: {e}")
        # Don't fail startup if migrations fail - tables should still be created
        pass

# Error handling
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
