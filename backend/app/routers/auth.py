from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.schemas.auth import UserCreate, UserResponse, Token
from app.models.user import User
from app.database import get_db
from app.dependencies import get_current_user
import jwt
import os
from datetime import datetime, timedelta
import logging
from app.crud.user import create_user, get_user_by_email
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.responses import RedirectResponse, JSONResponse
import json

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)

# OAuth setup
oauth = OAuth()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
FRONTEND_URL = os.getenv("FRONTEND_URL")

if not all([GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, FRONTEND_URL]):
    raise ValueError("Missing required environment variables for OAuth setup")

oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile',
        'prompt': 'select_account'
    },
    authorize_params={
        'access_type': 'offline'
    }
)

def create_access_token(data: dict):
    """Create JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    encoded_jwt = jwt.encode(
        to_encode,
        os.getenv("JWT_SECRET", "dev_jwt_secret"),
        algorithm="HS256"
    )
    return encoded_jwt

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    try:
        # Check if user already exists
        existing_user = get_user_by_email(db, user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        db_user = create_user(db, user)
        
        # Create access token using google_id as the subject
        access_token = create_access_token({"sub": db_user.google_id})
        
        return UserResponse(
            id=db_user.id,
            email=db_user.email,
            name=db_user.name,
            picture=db_user.picture,
            google_id=db_user.google_id,
            access_token=access_token,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user information."""
    try:
        # Refresh user data from database
        db_user = get_user_by_email(db, current_user.email)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Create fresh access token
        access_token = create_access_token({"sub": str(db_user.id)})
        
        return UserResponse(
            id=db_user.id,
            email=db_user.email,
            name=db_user.name,
            picture=db_user.picture,
            google_id=db_user.google_id,
            access_token=access_token,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user info: {str(e)}"
        )

@router.get("/google/authorize")
async def google_authorize(request: Request):
    """Start Google OAuth flow.
    
    This endpoint initiates the Google OAuth2 authorization flow by redirecting
    the user to Google's consent screen. The redirect_uri is dynamically
    generated based on the current request's base URL.
    """
    try:
        # Get the public URL from environment variable
        public_url = os.getenv("PUBLIC_URL", "http://localhost:8003")
        redirect_uri = f"{public_url}/auth/google/callback"
        
        # Configure OAuth client
        oauth.google.client_id = GOOGLE_CLIENT_ID
        oauth.google.client_secret = GOOGLE_CLIENT_SECRET
        oauth.google.authorize_url = 'https://accounts.google.com/o/oauth2/v2/auth'
        oauth.google.access_token_url = 'https://oauth2.googleapis.com/token'
        oauth.google.api_base_url = 'https://www.googleapis.com/oauth2/v3/'
        
        logger.info(f"Initiating Google OAuth flow with redirect URI: {redirect_uri}")
        return await oauth.google.authorize_redirect(
            request,
            redirect_uri,
            access_type='offline',
            prompt='consent'
        )
    except Exception as e:
        logger.error(f"Google authorization failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate Google OAuth flow: {str(e)}"
        )

@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    """Handle Google OAuth callback."""
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not fetch user info from Google"
            )
        
        # Create or update user
        user = UserCreate(
            email=user_info['email'],
            name=user_info['name'],
            google_id=user_info['sub'],
            picture=user_info.get('picture', '')
        )
        
        # Register user and get response with token
        db_user = await register(user, db)
        
        # Redirect to frontend with token
        return RedirectResponse(
            url=f"{FRONTEND_URL}/auth/callback?token={db_user.access_token}",
            status_code=status.HTTP_302_FOUND
        )
        
    except Exception as e:
        logger.error(f"Google callback failed: {e}")
        return RedirectResponse(
            url=f"{FRONTEND_URL}/login?error=authentication_failed",
            status_code=status.HTTP_302_FOUND
        )

@router.get("/healthz")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
