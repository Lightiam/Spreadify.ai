from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
from app.database import init_db
from app.routers import auth, streams, stripe, webrtc

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(title="Spreadify API")

# Configure CORS
cors_origins = eval(os.getenv("CORS_ORIGINS", '["http://localhost:5173"]'))
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(streams.router, prefix="/streams", tags=["streams"])
app.include_router(stripe.router, prefix="/stripe", tags=["stripe"])
app.include_router(webrtc.router, prefix="/webrtc", tags=["webrtc"])

# Health check endpoint
@app.get("/healthz")
async def health_check():
    return {"status": "healthy"}

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()

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
