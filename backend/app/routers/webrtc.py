from fastapi import APIRouter, WebSocket, HTTPException, status, Query, Depends
import jwt
from jwt.exceptions import InvalidTokenError
import os
import logging
import base64
import hashlib
from typing import Dict
import json
from app.dependencies import get_current_user, get_token_from_query

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

router = APIRouter(tags=["webrtc"])

# Store active connections
connections: Dict[str, WebSocket] = {}

def verify_websocket_key(key: str) -> str:
    """Verify and generate WebSocket accept key according to RFC 6455."""
    if not key:
        raise HTTPException(status_code=400, detail="Missing Sec-WebSocket-Key header")
    
    GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    accept = base64.b64encode(
        hashlib.sha1(f"{key}{GUID}".encode()).digest()
    ).decode()
    return accept

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(None)
):
    try:
        logger.info("New WebSocket connection attempt")
        logger.info(f"Headers: {websocket.headers}")
        
        # Get WebSocket key from headers
        ws_key = websocket.headers.get("sec-websocket-key")
        if not ws_key:
            logger.error("Missing Sec-WebSocket-Key header")
            await websocket.close(code=4000, reason="Missing Sec-WebSocket-Key header")
            return
            
        # Verify WebSocket key
        try:
            verify_websocket_key(ws_key)
        except Exception as e:
            logger.error(f"WebSocket key verification failed: {str(e)}")
            await websocket.close(code=4000, reason="Invalid Sec-WebSocket-Key header")
            return
            
        # Validate token with detailed logging
        logger.info(f"Received WebSocket connection request with token: {token[:10]}...")
        if not token:
            logger.error("No token provided in WebSocket connection")
            await websocket.close(code=4000, reason="No token provided")
            return
            
        try:
            # Load environment variables and decode JWT token with detailed logging
            from dotenv import load_dotenv
            load_dotenv()
            
            secret_key = os.getenv("JWT_SECRET", "dev_jwt_secret_key_replace_in_production")
            logger.info(f"Using JWT_SECRET from env (first 10 chars): {secret_key[:10] if secret_key else 'None'}")
            
            try:
                logger.info("Attempting to decode JWT token")
                payload = jwt.decode(
                    token,
                    secret_key,
                    algorithms=["HS256"]
                )
                logger.info(f"JWT token decoded successfully. Payload: {payload}")
                logger.info(f"Token decoded successfully. Subject: {payload.get('sub', 'unknown')}")
            except Exception as e:
                logger.error(f"Token decode error: {str(e)}")
                raise
            user_id = payload.get("sub")  # Email is used as user_id
            if not user_id:
                await websocket.close(code=4001, reason="Invalid token")
                return
        except InvalidTokenError:
            await websocket.close(code=4001, reason="Invalid token")
            return
            
        # Accept the connection
        await websocket.accept()
        logger.info(f"WebSocket connection accepted for user {user_id}")
        
        # Store the connection
        connections[user_id] = websocket
        logger.info(f"Active connections: {len(connections)}")
        
        try:
            while True:
                try:
                    # Handle both text messages and other WebSocket frames (ping/pong)
                    message = await websocket.receive()
                    logger.info(f"Received message type: {message['type']} from user {user_id}")
                    
                    if message["type"] == "websocket.disconnect":
                        logger.info(f"Client disconnected: {user_id}")
                        break
                        
                    if message["type"] == "websocket.receive":
                        data = message.get("text", message.get("bytes", ""))
                        logger.info(f"Received data from user {user_id}: {data}")
                        
                        try:
                            message_data = json.loads(data)
                            message_type = message_data.get("type")
                            
                            # Handle different message types
                            if message_type == "ping":
                                await websocket.send_json({
                                    "type": "pong",
                                    "data": message_data.get("data")
                                })
                                logger.info(f"Sent pong response to user {user_id}")
                            else:
                                await websocket.send_json({
                                    "type": "error",
                                    "data": f"Unknown message type: {message_type}"
                                })
                                logger.warning(f"Unknown message type from user {user_id}: {message_type}")
                        except json.JSONDecodeError:
                            logger.error(f"Invalid JSON message from user {user_id}: {data}")
                            await websocket.send_json({
                                "type": "error",
                                "data": "Invalid JSON message"
                            })
                    elif message["type"] == "websocket.pong":
                        logger.info(f"Received pong from user {user_id}")
                except Exception as msg_error:
                    logger.error(f"Error handling message from user {user_id}: {str(msg_error)}")
                    try:
                        await websocket.send_json({
                            "type": "error",
                            "data": "Internal server error"
                        })
                    except Exception:
                        logger.error("Failed to send error message")
                        break
        except Exception as e:
            logger.error(f"Error in websocket loop: {str(e)}")
        finally:
            # Clean up connection
            if user_id in connections:
                del connections[user_id]
                logger.info(f"Removed connection for user {user_id}")
            try:
                await websocket.close()
            except Exception as close_error:
                logger.error(f"Error closing websocket: {str(close_error)}")
    except Exception as e:
        logger.error(f"WebSocket connection error: {str(e)}")
        try:
            await websocket.close(code=4002, reason="Internal server error")
        except Exception as close_error:
            logger.error(f"Error closing websocket: {str(close_error)}")

@router.get("/healthz")
async def health_check():
    return {"status": "healthy", "connections": len(connections)}
