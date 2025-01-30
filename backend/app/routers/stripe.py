from fastapi import APIRouter, HTTPException, status

router = APIRouter(tags=["stripe"])

@router.get("/healthz")
async def health_check():
    return {"status": "healthy"}
