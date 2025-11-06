import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Header

import utils
from config import PORT
from role import Role

# --- FastAPI app ---
app = FastAPI()

# --- Connected clients ---
clients: dict[Role, WebSocket] = {}

# --- HTTP endpoint to get JWT using API key ---
@app.get("/token")
async def get_token(x_api_key: str = Header(...)):
    """
    Endpoint to get a JWT token using an API key.

    :param x_api_key: The API key provided by the client.
    :return: A dictionary containing the JWT token.
    """

    return {"token": utils.generate_jwt(x_api_key)}

# --- WebSocket endpoint ---
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str):
    """
    WebSocket endpoint to handle incoming messages.

    :param websocket: The WebSocket connection.
    :param token: The JWT token provided by the client.
    """

    try:
        # Verify JWT
        payload = utils.verify_jwt(token)
        # Accept connection
        await websocket.accept()
        # Register client
        clients[Role.from_str(payload.get("role"))] = websocket
        print(f"Client connected: {payload.get("sub")} with role {payload.get("role")}")
    except HTTPException:
        await websocket.close(code=1008)
        return

    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            # Handle message
            await utils.handle_message(data, clients, payload.get("role"))
    except WebSocketDisconnect:
        print(f"Client disconnected: {payload.get("sub")}")
        # Unregister client
        if payload["role"] in clients:
            del clients[payload["role"]]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(PORT))
