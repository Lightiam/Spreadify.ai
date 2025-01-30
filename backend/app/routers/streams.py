from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/streams", tags=["streams"])

@router.get("/healthz")
async def health_check():
    return {"status": "healthy"}
