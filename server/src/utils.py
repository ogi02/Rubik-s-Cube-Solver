# Python imports
import asyncio
import logging
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, WebSocket
from jose import jwt, JWTError

# Project imports
import config
from role import Role


def generate_jwt(api_key: str) -> str:
    """
    Generate a JWT token if the provided API key is valid.

    :param api_key: The API key to validate.
    :return: A JWT token.
    :raise HTTPException: If the API key is invalid.
    """

    # Generate expiration time claim
    exp = datetime.now(timezone.utc) + timedelta(hours=2)

    match api_key:
        case config.SOLVER_API_KEY:
            claims = {
                "sub": f"CLIENT_{Role.SOLVER.value}",
                "role": Role.SOLVER.value,
                "exp": int(exp.timestamp())
            }
            logging.info(f"Generating JWT token: {claims}")
            return jwt.encode(claims, config.JWT_SECRET, algorithm=config.ALGORITHM)
        case config.VISUALIZER_API_KEY:
            claims = {
                "sub": f"CLIENT_{Role.VISUALIZER.value}",
                "role": Role.VISUALIZER.value,
                "exp": int(exp.timestamp())
            }
            logging.info(f"Generating JWT token: {claims}")
            return jwt.encode(claims, config.JWT_SECRET, algorithm=config.ALGORITHM)
        case _:
            logging.error(f"Unknown API key {api_key}")
            raise HTTPException(status_code=401, detail="Invalid API key")


def verify_jwt(token: str) -> dict:
    """
    Verify a JWT token and return its payload.

    :param token: The JWT token to verify.
    :return: The payload of the JWT token if valid.
    :raise HTTPException: If the token is invalid.
    """

    try:
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=[config.ALGORITHM])
        return payload
    except JWTError:
        logging.error("Invalid JWT token")
        raise HTTPException(status_code=401, detail="Invalid token")


async def register_client(role: Role, websocket: WebSocket, known_clients: dict[Role, WebSocket], clients_lock: asyncio.Lock) -> None:
    """
    Register a connected client.

    :param role: The role of the client.
    :param websocket: The WebSocket connection of the client.
    :param known_clients: A dictionary mapping roles to the connected WebSocket clients.
    :param clients_lock: An asyncio lock to ensure thread-safe access to known_clients.
    :raise HTTPException: If a client with the same role is already connected.
    """

    async with clients_lock:
        # Check if a client with the same role is already connected
        if role in known_clients:
            logging.warning(f"Client with role {role.value} is already connected")
            raise HTTPException(status_code=400, detail=f"Client with role {role.value} is already connected")
        # Accept connection
        await websocket.accept()
        # Register client
        known_clients[role] = websocket
        logging.info(f"Registered client with role {role.value}")


async def unregister_client(role: Role, known_clients: dict[Role, WebSocket], clients_lock: asyncio.Lock) -> None:
    """
    Unregister a disconnected client.

    :param role: The role of the client.
    :param known_clients: A dictionary mapping roles to the connected WebSocket clients.
    :param clients_lock: An asyncio lock to ensure thread-safe access to known_clients.
    """

    async with clients_lock:
        if role in known_clients:
            del known_clients[role]
            logging.info(f"Unregistered client with role {role.value}")
        else:
            logging.warning(f"Tried to unregister non-existent client with role {role.value}")


async def handle_message(message_data: dict, known_clients: dict[Role, WebSocket], sender_role: Role) -> None:
    """
    Handle an incoming message and route it to the appropriate clients.

    :param message_data: The data of the incoming message.
    :param known_clients: A dictionary mapping roles to the connected WebSocket clients.
    :param sender_role: The role of the sender.
    """

    if sender_role == Role.SOLVER:
        # Route message to the visualizer
        visualizer_ws: WebSocket = known_clients.get(Role.VISUALIZER, None)
        if not visualizer_ws:
            logging.warning("No visualizer connected to send the message to")
            return
        logging.info(f"Sending to visualizer: {message_data}")
        await visualizer_ws.send_json(message_data)
    elif sender_role == Role.VISUALIZER:
        # Route message to the solver
        solver_ws: WebSocket = known_clients.get(Role.SOLVER, None)
        if not solver_ws:
            logging.warning("No solver connected to send the message to")
            return
        logging.info(f"Sending to solver: {message_data}")
        await solver_ws.send_json(message_data)
    else:
        logging.warning("Invalid sender role")
