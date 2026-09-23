r"""
End-to-end demo of the solver driving the visualizer through the WebSocket server.

It creates a cube of the size given by CUBE_SIZE, scrambles it, sends the scrambled state to the
server as a `cube_state` message, solves the cube and sends the solution as an `apply_moves` message,
then disconnects. Every step prints a numbered header and pauses afterwards, so the output can be read
alongside the animation in the visualizer.

The solution is asked for step by step, and for a big cube the demo turns the view between the steps so
the face each one works on comes forward. The rotations add up to a full turn, so the cube is left
facing the way it started.

Every size ends up solved. A 4x4 or larger cube is first reduced to a 3x3 - all six centers built and
all twelve edges paired, with the parities fixed - and then solved as a 3x3, all within one solution.

The server must be running and a visualizer must be connected to it, otherwise the messages are
relayed nowhere.

With Docker, bring up the server and the visualizer, open http://localhost:5173, then run the demo.
The cube size comes from CUBE_SIZE in the shell or the repository-root .env, 3 if unset:

    docker compose up -d
    docker compose run --rm playground
    docker compose run --rm -e CUBE_SIZE=5 playground

Without Docker, install the two libraries from Test PyPI, with the public index available for their
dependencies:

    pip install -r playground/requirements.txt \
        -i https://test.pypi.org/simple/ \
        --extra-index-url https://pypi.org/simple/

Set the solver API key of the server, and the host, port and cube size if they are not the defaults:

    export SOLVER_API_KEY=<the server's SOLVER_API_KEY>
    export CUBE_SIZE=4

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

# The size of the cube to scramble and solve: 2, 3, or 4 and up for the big-cube solver
CUBE_SIZE = int(os.getenv("CUBE_SIZE", "3"))

if not API_KEY:
    raise SystemExit("SOLVER_API_KEY is not set")

if CUBE_SIZE < 2:
    raise SystemExit(f"CUBE_SIZE must be 2 or more, got {CUBE_SIZE}")

# Seconds to wait for the connection to be established before the first message is sent
CONNECT_DELAY = 1.0

# Seconds to pause after each step, so the visualizer has time to show what it was sent
STEP_DELAY = 2.0

# The view rotation sent before each step of a big-cube solve, so the faces that step works on turn
# towards the viewer. A center is built on one face out of pieces gathered on another, and both are
# worth watching, so each turn brings the pair of them into view. In the orientation the cube starts
# in they are: yellow gathered at the front and built underneath, white at the front and on top,
# green on the right and at the front, red at the back and on the right, and the last two behind and
# to the left. The third center needs no turn, since the second leaves both its faces in view.
#
# From the third center on the cube is only turned about its vertical axis, so white stays on top and
# yellow underneath and the solve is watched the way it is usually held.
#
# The edges are paired all round the cube rather than on one face, so their turn brings forward the
# two slots the pairs are actually made in. The rotations add up to a full turn, leaving the cube as
# it started, white on top and green at the front.
#
# They change only the point of view. A rotation never moves a piece, so the moves after it still
# turn exactly the faces the solver meant.
BIG_CUBE_VIEWS: dict[str, str] = {
    "1st center": "x",
    "2nd center": "x'",
    "4th center": "y",
    "last 2 centers": "y",
    "edges": "y'",
    "3x3 stage": "y'",
}

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


def moves_with_views(steps: dict[str, Algorithm]) -> list[str]:
    """
    Lays the steps out as one list of moves, turning the view before each one on a big cube.

    A 2x2 and a 3x3 are solved entirely on the faces already in view, so they are sent as they are.

    :param steps: The solution of each step, by name
    :return: The moves to send, with the view rotations in place
    """

    moves: list[str] = []

    for name, algorithm in steps.items():
        view = BIG_CUBE_VIEWS.get(name, "") if CUBE_SIZE >= 4 else ""
        moves += f"{view} {algorithm}".split()

    return moves


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
    solver = create_solver(cube)
    steps = solver.solve(steps=True)
    print(f"Solver: {type(solver).__name__}")
    for name, algorithm in steps.items():
        print(f"{name:>16}: {len(algorithm.moves):4d} moves")
    print(f"Solved {CUBE_SIZE}x{CUBE_SIZE}:")
    print(cube)
    await asyncio.sleep(STEP_DELAY)

    announce("Sending the solution")
    moves = moves_with_views(steps)
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
