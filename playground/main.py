import json

from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.rotator import Rotator
from rubik_cube_solver.scramble.scrambler import Scrambler

from rubik_cube_websocket_client.client import WebSocketClient

async def main():
    # Initialize cube, rotator, and scrambler
    cube_size = 3
    cube = Cube(size=cube_size)
    rotator = Rotator(cube)
    scrambler = Scrambler()

    # Generate a scramble
    scramble_moves = scrambler.generate_scramble(cube_size=cube_size)

    # Print the scramble
    print(f"Scramble: {" ".join(str(move) for move in scramble_moves)}")

    # Apply each move to the cube
    for move in scramble_moves:
        rotator.turn(move)

    # Print the cube state
    print(f"\nScrambled cube state: \n{cube}\n")

    # Connect to the server via WebSocket
    client = WebSocketClient(
        host="127.0.0.1", port=8080, secure=False,
        api_key="2ba79446-5754-4123-858c-ed863efae315"
    )

    client.authenticate()

    task = asyncio.create_task(client.run())

    state = {}
    for layer, stickers in cube.layers.items():
        state[str(layer.name)] = [sticker.value for sticker in stickers]

    message = {
        "type": "cube_state",
        "data": {
            "dimensions": cube.size,
            "state": state
        }
    }

    message2 = {
        "type": "apply_moves",
        "data": {
            "moves": [str(move) for move in scramble_moves]
        }
    }

    print(json.dumps(message2, indent = 4))

    await client.send_message(message2)

    await asyncio.gather(task)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
