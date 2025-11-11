# Python imports
import asyncio
import json
import logging

import uvicorn
from fastapi import FastAPI, Header, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# Project imports
import config
import utils
from role import Role

# FastAPI app
app = FastAPI()

# Allow Vite dev server origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connected clients
clients: dict[Role, WebSocket] = {}
clients_lock = asyncio.Lock()


# HTTP endpoint to get JWT using API key
@app.get("/token")
async def get_token(x_api_key: str = Header(...)) -> dict[str, str]:
    """
    Endpoint to get a JWT token using an API key.

    :param x_api_key: The API key provided by the client.
    :return: A dictionary containing the JWT token.
    """

    return {"token": utils.generate_jwt(x_api_key)}


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str) -> None:
    """
    WebSocket endpoint to handle incoming messages.

    :param websocket: The WebSocket connection.
    :param token: The JWT token provided by the client.
    """

    try:
        # Verify JWT
        payload = utils.verify_jwt(token)
        # Try to register client
        role = Role.from_str(payload.get("role"))
        await utils.register_client(role, websocket, clients, clients_lock)
    except (HTTPException, ValueError) as e:
        await websocket.close(code=1008, reason=str(e))
        return

    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            data = json.loads(data)
            # Check for disconnect message
            if data.get("type") == "disconnect":
                logging.info(f"Client requested disconnect: {payload.get('sub')}")
                await websocket.close(code=1000, reason="Client requested disconnect")
                # Unregister client
                await utils.unregister_client(role, clients, clients_lock)
                return
            # Handle message
            await utils.handle_message(data, clients, role)
    except WebSocketDisconnect:
        logging.info(f"Client disconnected: {payload.get('sub')}")
        # Unregister client
        await utils.unregister_client(role, clients, clients_lock)
    except Exception as e:
        logging.error(f"Error handling message from {payload.get('sub')}: {e}")
        await websocket.close(code=1003, reason=str(e))
        # Unregister client
        await utils.unregister_client(role, clients, clients_lock)


if __name__ == "__main__":
    uvicorn.run(app, host=config.HOST, port=int(config.PORT))
