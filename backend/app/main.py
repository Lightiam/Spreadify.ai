from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from datetime import datetime
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

# Configure session middleware (required for OAuth)
from starlette.middleware.sessions import SessionMiddleware
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("JWT_SECRET", "dev_jwt_secret_key_replace_in_production"),
    max_age=3600  # 1 hour
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
    prefix="",  # Remove prefix to allow direct /ws access
    tags=["webrtc"],
    dependencies=[Depends(get_db)]
)

# Health check endpoint with database verification
@app.get("/healthz")
async def health_check(db: Session = Depends(get_db)):
    try:
        health_status = {
            "status": "healthy",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "tests": {}
        }

        # Database connection test
        try:
            db.execute(text("SELECT 1"))
            health_status["tests"]["database_connection"] = {
                "status": "passed",
                "message": "Successfully connected to database"
            }
        except Exception as db_err:
            print(f"Database connection error: {str(db_err)}")
            health_status["tests"]["database_connection"] = {
                "status": "failed",
                "error": str(db_err)
            }
            health_status["status"] = "error"
            return health_status

        # CRUD operations test
        try:
            from app.crud.user import create_user, get_user_by_email, update_user, delete_user
            from app.schemas.auth import UserCreate, UserUpdate
            
            crud_results = []
            
            # Test Create
            test_user = UserCreate(
                email="test@example.com",
                name="Test User",
                google_id="test123",
                picture="https://example.com/pic.jpg"
            )
            db_user = create_user(db, test_user)
            crud_results.append(("create", True, "User created successfully"))
            
            # Test Read
            found_user = get_user_by_email(db, "test@example.com")
            if not found_user:
                raise Exception("Failed to retrieve created user")
            crud_results.append(("read", True, "User retrieved successfully"))
            
            # Test Update
            update_data = UserUpdate(name="Updated Test User")
            updated_user = update_user(db, found_user.id, update_data)
            if updated_user.name != "Updated Test User":
                raise Exception("User update failed")
            crud_results.append(("update", True, "User updated successfully"))
            
            # Test Delete
            deleted_user = delete_user(db, found_user.id)
            if not deleted_user:
                raise Exception("User deletion failed")
            crud_results.append(("delete", True, "User deleted successfully"))
            
            # Verify Deletion
            deleted_check = get_user_by_email(db, "test@example.com")
            if deleted_check:
                raise Exception("User still exists after deletion")
            crud_results.append(("verify_deletion", True, "Deletion verified"))
            
            # Add CRUD test results
            health_status["tests"]["crud_operations"] = {
                "status": "passed",
                "operations": {op: {"status": status, "message": msg} for op, status, msg in crud_results}
            }
            
        except Exception as crud_err:
            print(f"CRUD test error: {str(crud_err)}")
            health_status["tests"]["crud_operations"] = {
                "status": "failed",
                "error": str(crud_err)
            }
            health_status["status"] = "error"
        
        # WebSocket connection count
        try:
            from app.routers.webrtc import connections
            health_status["tests"]["websocket"] = {
                "status": "passed",
                "active_connections": len(connections)
            }
        except Exception as ws_err:
            health_status["tests"]["websocket"] = {
                "status": "failed",
                "error": str(ws_err)
            }
        
        return health_status

    except Exception as e:
        print(f"Health check error: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat()
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
