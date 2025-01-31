import asyncio
import websockets
import json
import sys
import os
from dotenv import load_dotenv

load_dotenv()

async def test_websocket_connection():
    # Get token from command line or environment
    token = sys.argv[1] if len(sys.argv) > 1 else os.getenv("TEST_TOKEN")
    if not token:
        print("Please provide a token as argument or set TEST_TOKEN environment variable")
        return

    uri = f"ws://localhost:8000/ws?token={token}"
    print(f"Connecting to {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to WebSocket server")
            
            # Send a ping message
            ping_message = {
                "type": "ping",
                "data": "test ping"
            }
            await websocket.send(json.dumps(ping_message))
            print(f"Sent: {ping_message}")
            
            # Wait for response
            response = await websocket.recv()
            print(f"Received: {response}")
            
            # Keep connection alive for a few seconds
            await asyncio.sleep(5)
            
    except websockets.exceptions.ConnectionClosed as e:
        print(f"Connection closed: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket_connection())
