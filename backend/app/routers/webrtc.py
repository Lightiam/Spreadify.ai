from fastapi import APIRouter, WebSocket, HTTPException, status

router = APIRouter(tags=["webrtc"])

@router.get("/healthz")
async def health_check():
    return {"status": "healthy"}
