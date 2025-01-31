import asyncio
import websockets
import json
import sys
import os
import logging
import pytest
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

@pytest.mark.asyncio
async def test_websocket_connection():
    """Test WebSocket connection with authentication and ping/pong."""
    try:
        # Get token from environment or generate one
        token = os.getenv("TEST_TOKEN")
        if not token:
            from generate_test_ws_token import generate_test_token
            token = generate_test_token()
            logger.info("Generated new test token")

        uri = f"ws://localhost:8000/ws?token={token}"
        logger.info(f"Attempting connection to {uri}")
        
        async with websockets.connect(uri) as websocket:
            logger.info("Successfully connected to WebSocket server")
            
            # Send a ping message
            ping_message = {
                "type": "ping",
                "data": "test ping",
                "timestamp": str(asyncio.get_event_loop().time())
            }
            await websocket.send(json.dumps(ping_message))
            logger.info(f"Sent ping message: {ping_message}")
            
            # Wait for response with timeout
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                response_data = json.loads(response)
                logger.info(f"Received response: {response_data}")
                
                # Verify response
                if response_data.get("type") != "pong":
                    raise ValueError(f"Expected pong response, got: {response_data.get('type')}")
                    
                logger.info("WebSocket test completed successfully")
                return True
                
            except asyncio.TimeoutError:
                logger.error("Timeout waiting for server response after 5 seconds")
                raise
            
    except websockets.exceptions.ConnectionClosed as e:
        logger.error(f"WebSocket connection closed unexpectedly: {e}")
        raise
    except Exception as e:
        logger.error(f"WebSocket test failed: {str(e)}")
        raise
    finally:
        logger.info("WebSocket test completed")

if __name__ == "__main__":
    try:
        asyncio.run(test_websocket_connection())
    except Exception as e:
        logger.error(f"WebSocket test failed: {str(e)}")
        sys.exit(1)
