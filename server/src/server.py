# Python imports
import asyncio
import logging
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Header

# Project imports
import config
import utils
from role import Role

# FastAPI app
app = FastAPI()

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
            # Handle message
            await utils.handle_message(data, clients, role)
    except ValueError as e:
        logging.error(f"Error handling message from {payload.get('sub')}: {e}")
        await websocket.close(code=1003, reason=str(e))
    except WebSocketDisconnect:
        logging.info(f"Client disconnected: {payload.get('sub')}")
        # Unregister client
        await utils.unregister_client(role, clients, clients_lock)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(config.PORT))
