r"""
End-to-end demo of the solver driving the visualizer through the WebSocket server.

It creates a cube of the size given by CUBE_SIZE, scrambles it, sends the scrambled state to the
server as a `cube_state` message, solves the cube and sends the solution as an `apply_moves` message,
then disconnects. Every step prints a numbered header and pauses afterwards, so the output can be read
alongside the animation in the visualizer.

A 2x2 or a 3x3 ends up solved. A 4x4 or larger cube ends up reduced to a 3x3 - all six centers built
and all twelve edges paired, with the parities fixed - but the corners and the edges are not put in
place, since the big-cube solver does not go beyond the parity step yet. For those sizes the demo
also prints which centers are built and which edges are paired.

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
from rubik_cube_solver.enums.EdgeSlot import EdgeSlot
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.scramble.scrambler import Scrambler
from rubik_cube_solver.solve.cube_nxn.edges import is_paired
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

# The smallest cube the big-cube solver handles, which only reduces the cube to a 3x3
BIG_CUBE_SIZE = 4

if not API_KEY:
    raise SystemExit("SOLVER_API_KEY is not set")

if CUBE_SIZE < 2:
    raise SystemExit(f"CUBE_SIZE must be 2 or more, got {CUBE_SIZE}")

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


def built_centers(cube: Cube) -> dict[Layer, str]:
    """
    Returns the faces whose whole center is a single colour, with that colour's name.

    :param cube: The cube
    :return: The name of the colour of every finished center, by face
    """

    size = cube.size
    built = {}

    for face in Layer:
        colors = {cube.layers[face][row * size + col] for row in range(1, size - 1) for col in range(1, size - 1)}
        if len(colors) == 1:
            built[face] = colors.pop().name

    return built


def paired_edges(cube: Cube) -> list[EdgeSlot]:
    """
    Returns the edge slots whose wings all show the same two colours.

    :param cube: The cube
    :return: The slots holding a paired edge
    """

    return [slot for slot in EdgeSlot if is_paired(cube, slot)]


def print_reduction(cube: Cube) -> None:
    """
    Prints which centers of a big cube are built and which of its edges are paired.

    :param cube: The big cube, after the big-cube solver has run
    :return: None
    """

    print("Centers built:")
    for face, color in built_centers(cube).items():
        print(f"  {face.name:<6} {color}")

    paired = paired_edges(cube)
    print(f"Edges paired ({len(paired)}): {' '.join(slot.name for slot in paired)}")


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

    is_big_cube = CUBE_SIZE >= BIG_CUBE_SIZE

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

    announce("Reducing the cube to a 3x3" if is_big_cube else "Solving the cube")
    solver = create_solver(cube)
    solution = solver.solve()
    print(f"Solver: {type(solver).__name__}")
    print(f"Solution ({len(solution.moves)} moves): {solution}")
    print(f"{CUBE_SIZE}x{CUBE_SIZE} {'reduced to a 3x3' if is_big_cube else 'solved'}:")
    print(cube)
    if is_big_cube:
        print_reduction(cube)
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
