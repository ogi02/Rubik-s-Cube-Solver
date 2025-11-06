from fastapi import HTTPException, WebSocket
from jose import jwt, JWTError

from role import Role
import config

def generate_jwt(api_key: str) -> str:
    """
    Generate a JWT token if the provided API key is valid.

    :param api_key: The API key to validate.
    :return: A JWT token.
    """

    match api_key:
        case config.SOLVER_API_KEY:
            claims = {
                "sub": f"CLIENT_{Role.SOLVER.value}",
                "role": Role.SOLVER.value
            }
            return jwt.encode(claims, config.JWT_SECRET, algorithm=config.ALGORITHM)
        case config.VISUALIZER_API_KEY:
            claims = {
                "sub": f"CLIENT_{Role.VISUALIZER.value}",
                "role": Role.VISUALIZER.value,
            }
            return jwt.encode(claims, config.JWT_SECRET, algorithm=config.ALGORITHM)
        case _:
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
        print(payload)
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def handle_message(message_data: dict, known_clients: dict[Role, WebSocket], sender_role: Role):
    """
    Handle an incoming message and route it to the appropriate clients.

    :param message_data: The data of the incoming message.
    :param known_clients: A dictionary mapping roles to lists of connected WebSocket clients.
    :param sender_role: The role of the sender.
    """

    if sender_role == Role.SOLVER.value:
        # Route message to the visualizer
        visualizer_ws: WebSocket = known_clients[Role.SOLVER]
        print(f"Sending to visualizer: {message_data}")
        await visualizer_ws.send_json(message_data)
    elif sender_role == Role.VISUALIZER.value:
        # Route message to the solver
        solver_ws: WebSocket = known_clients[Role.SOLVER]
        print(f"Sending to solver: {message_data}")
        await solver_ws.send_json(message_data)
    else:
        print("Invalid sender role")
