from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
import stripe
import os

router = APIRouter(tags=["stripe"])

@router.post("/create-checkout-session")
async def create_checkout_session(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create Stripe checkout session."""
    try:
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "test_key")
        
        # For testing, return mock response if using test key
        if stripe.api_key == "test_key":
            return {
                "id": "test_session",
                "url": request.get("success_url")
            }
            
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price": request.get("price_id"),
                "quantity": 1,
            }],
            mode="subscription",
            success_url=request.get("success_url"),
            cancel_url=request.get("cancel_url"),
            customer_email=current_user.email
        )
        return session
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/healthz")
async def health_check():
    return {"status": "healthy"}
