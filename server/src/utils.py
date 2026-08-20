# Python imports
import asyncio
import hmac
import logging
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, WebSocket
from jose import JWTError, jwt

# Project imports
import config
from role import Role
from validation import validate_message

# Lifetime of an issued JWT token
JWT_LIFETIME = timedelta(seconds=60)


def _build_jwt(role: Role) -> str:
    """
    Build and encode a JWT token for the given role.

    :param role: The Role to encode into the token claims.
    :return: A JWT token.
    """

    exp = datetime.now(timezone.utc) + JWT_LIFETIME
    claims = {"sub": f"CLIENT_{role.value}", "role": role.value, "exp": int(exp.timestamp())}
    logging.info(f"Generating JWT token: {claims}")
    return jwt.encode(claims, config.JWT_SECRET, algorithm=config.ALGORITHM)


def generate_jwt(api_key: str) -> str:
    """
    Generate a JWT token if the provided API key is valid.

    :param api_key: The API key to validate.
    :return: A JWT token.
    :raise HTTPException: If the API key is invalid.
    """

    if hmac.compare_digest(api_key, config.SOLVER_API_KEY):
        return _build_jwt(Role.SOLVER)
    if hmac.compare_digest(api_key, config.VISUALIZER_API_KEY):
        return _build_jwt(Role.VISUALIZER)

    logging.error("Rejected token request: unknown API key")
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


async def register_client(
    role: Role, websocket: WebSocket, known_clients: dict[Role, WebSocket], clients_lock: asyncio.Lock
) -> None:
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
    Validate an incoming message and route it from the solver to the visualizer.

    :param message_data: The data of the incoming message.
    :param known_clients: A dictionary mapping roles to the connected WebSocket clients.
    :param sender_role: The role of the sender.
    """

    try:
        validate_message(message_data, sender_role)
    except ValueError as e:
        logging.warning(f"Dropping invalid message from {sender_role.value}: {e}")
        return

    # Route message to the visualizer
    visualizer_ws: WebSocket = known_clients.get(Role.VISUALIZER, None)
    if not visualizer_ws:
        logging.warning("No visualizer connected to send the message to")
        return
    logging.info(f"Sending to visualizer: {message_data}")
    await visualizer_ws.send_json(message_data)
