r"""
End-to-end demo of the solver driving the visualizer through the WebSocket server.

It creates a cube, scrambles it, sends the scrambled state to the server as a `cube_state`
message, solves the cube and sends the solution as an `apply_moves` message, then disconnects.
Every step prints a numbered header and pauses afterwards, so the output can be read alongside the
animation in the visualizer.

The server must be running and a visualizer must be connected to it, otherwise the messages are
relayed nowhere.

Install the two libraries from Test PyPI, with the public index available for their dependencies:

    pip install -r playground/requirements.txt \
        -i https://test.pypi.org/simple/ \
        --extra-index-url https://pypi.org/simple/

Set the solver API key of the server, and the host and port if they are not the defaults:

    export SOLVER_API_KEY=<the server's SOLVER_API_KEY>

Then run it with:

    python playground/solver_visualizer_demo.py
"""

# Python imports
import asyncio
import itertools
import os

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.cube_rotation.rotator import Rotator
from rubik_cube_solver.scramble.scrambler import Scrambler
from rubik_cube_solver.solve.solver import create_solver
from rubik_cube_websocket_client.client import WebSocketClient
from rubik_cube_websocket_client.messages import apply_moves, cube_state, disconnect

# The server to connect to, matching the server's own HOST and PORT defaults
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8080"))
SECURE = False

# The API key the server issues solver tokens for
API_KEY = os.getenv("SOLVER_API_KEY", "solver")

CUBE_SIZE = 4

if not API_KEY:
    raise SystemExit("SOLVER_API_KEY is not set")

# Seconds to wait for the connection to be established before the first message is sent
CONNECT_DELAY = 1.0

# Seconds to pause after each step, so the visualizer has time to show what it was sent
STEP_DELAY = 2.0

# Numbers the step headers in the order they are actually printed, so they cannot drift
_step_numbers = itertools.count(start=1)


def announce(title: str) -> None:
    """
    Prints a numbered, separated header for the step that is about to run.

    :param title: The title of the step
    :return: None
    """

    print("=" * 100)
    print(f"[{next(_step_numbers)}] {title}")
    print("=" * 100)
    print()


def scramble_a_cube() -> tuple[Cube, Algorithm]:
    """
    Creates a cube and applies a randomly generated scramble to it.

    :return: The scrambled cube and the scramble that was applied
    """

    cube = Cube(size=CUBE_SIZE)
    scramble = Algorithm(Scrambler().generate_scramble(cube.size))
    Rotator(cube).apply(scramble)

    return cube, scramble


def connect_to_server() -> WebSocketClient:
    """
    Builds a solver client and authenticates it with the server.

    :return: The authenticated client
    """

    client = WebSocketClient(host=HOST, port=PORT, secure=SECURE, api_key=API_KEY)
    client.authenticate()

    if not client.token:
        raise SystemExit(f"Could not authenticate with the server at {HOST}:{PORT}")

    return client


async def run_demo() -> None:
    """
    Runs the whole demo: scramble, connect, send the state, solve, send the solution, disconnect.

    :return: None
    """

    announce(f"Creating and scrambling a {CUBE_SIZE}x{CUBE_SIZE} cube")
    cube, scramble = scramble_a_cube()
    print(f"Scramble ({len(scramble.moves)} moves): {scramble}")
    print(f"Scrambled {CUBE_SIZE}x{CUBE_SIZE}:")
    print(cube)
    await asyncio.sleep(STEP_DELAY)

    announce("Connecting to the server")
    client = connect_to_server()
    connection = asyncio.create_task(client.run())
    await asyncio.sleep(CONNECT_DELAY)
    print(f"Connected to {HOST}:{PORT} as the solver")
    await asyncio.sleep(STEP_DELAY)

    announce("Sending the scrambled cube state")
    await client.send_message(cube_state(**cube.state()))
    print("Sent a cube_state message with the scrambled cube")
    await asyncio.sleep(STEP_DELAY)

    announce("Solving the cube")
    solution = create_solver(cube).solve()
    print(f"Solution ({len(solution.moves)} moves): {solution}")
    print(f"The {CUBE_SIZE}x{CUBE_SIZE} after the solution:")
    print(cube)
    await asyncio.sleep(STEP_DELAY)

    announce("Sending the solution")
    moves = [str(move) for move in solution.moves]
    await client.send_message(apply_moves(moves))
    print(f"Sent an apply_moves message with {len(moves)} moves")
    await asyncio.sleep(STEP_DELAY)

    announce("Disconnecting")
    await client.send_message(disconnect())
    await asyncio.sleep(STEP_DELAY)
    await client.close()
    await connection
    print("Demo finished")


def main() -> None:
    """
    Entry point of the demo.

    :return: None
    """

    asyncio.run(run_demo())


if __name__ == "__main__":
    main()
