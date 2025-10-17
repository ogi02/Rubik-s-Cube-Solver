from cube import Cube
from cube_rotation.rotator import Rotator
from enums.Direction import Direction
from enums.Layer import Layer

def main():
    # Create a Rubik's Cube
    cube = Cube(3)
    rotator = Rotator(cube)

    # U R' L2 F U2 B' D L' R2 F' U B2 D' L R' F2 U' B D2 L'

    # Sequence of 20 moves
    moves = [
        (Layer.UP, 1, Direction.CW),
        (Layer.RIGHT, 1, Direction.CCW),
        (Layer.LEFT, 1, Direction.DOUBLE),
        (Layer.FRONT, 1, Direction.CW),
        (Layer.UP, 1, Direction.DOUBLE),
        (Layer.BACK, 1, Direction.CCW),
        (Layer.DOWN, 1, Direction.CW),
        (Layer.LEFT, 1, Direction.CCW),
        (Layer.RIGHT, 1, Direction.DOUBLE),
        (Layer.FRONT, 1, Direction.CCW),
        (Layer.UP, 1, Direction.CW),
        (Layer.BACK, 1, Direction.DOUBLE),
        (Layer.DOWN, 1, Direction.CCW),
        (Layer.LEFT, 1, Direction.CW),
        (Layer.RIGHT, 1, Direction.CCW),
        (Layer.FRONT, 1, Direction.DOUBLE),
        (Layer.UP, 1, Direction.CCW),
        (Layer.BACK, 1, Direction.CW),
        (Layer.DOWN, 1, Direction.DOUBLE),
        (Layer.LEFT, 1, Direction.CCW),
    ]

    # Apply the moves
    for i, (layer, slice_index, direction) in enumerate(moves, 1):
        print(f"Move {i}: {layer}, {direction}")
        rotator.turn(layer, slice_index, direction)

    # Print final cube state
    print("Final cube state:")
    print(cube)


def main2():
    # Create a Rubik's Cube
    cube = Cube(4)
    rotator = Rotator(cube)

    # U Rw' F2 Lw2 D' B U2 L' Fw R' D2 Lw' B2 U' R2 Fw' D Lw2 Bw'
    # U2 R F2 Rw D' L B2 Uw' F' R2 Lw D2 B R' Fw U2 Lw Bw' D

    # Example mapping function
    face_map = {
        "U": Layer.UP, "D": Layer.DOWN, "L": Layer.LEFT, "R": Layer.RIGHT,
        "F": Layer.FRONT, "B": Layer.BACK
    }

    direction_map = {
        "": Direction.CW,  # normal
        "'": Direction.CCW,
        "2": Direction.DOUBLE
    }

    # Manual mapping of scramble moves
    scramble_moves = [
        ("U", 1, ""), ("R", 2, "'"), ("F", 1, "2"), ("L", 2, "2"), ("D", 1, "'"),
        ("B", 1, ""), ("U", 1, "2"), ("L", 1, "'"), ("F", 2, ""), ("R", 1, "'"),
        ("D", 1, "2"), ("L", 2, "'"), ("B", 1, "2"), ("U", 1, "'"), ("R", 1, "2"),
        ("F", 2, "'"), ("D", 1, ""), ("L", 2, ""), ("B", 2, "'"), ("U", 1, "2"),
        ("R", 1, ""), ("F", 1, "2"), ("R", 2, ""), ("D", 1, "'"), ("L", 1, ""),
        ("B", 1, "2"), ("U", 2, "'"), ("F", 1, "'"), ("R", 1, "2"), ("L", 2, ""),
        ("D", 1, "2"), ("B", 1, ""), ("R", 1, "'"), ("F", 2, ""), ("U", 1, "2"),
        ("L", 2, ""), ("B", 2, "'"), ("D", 1, "")
    ]

    # Apply the scramble
    for face, layers, suffix in scramble_moves:
        rotator.turn(face_map[face], layers, direction_map[suffix])

    # Print final cube state
    print("Final cube state:")
    print(cube)


if __name__ == "__main__":
    main2()
