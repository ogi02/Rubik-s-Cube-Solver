from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.rotator import Rotator
from rubik_cube_solver.cube_rotation.move import Move
from rubik_cube_solver.enums import Rotation
from rubik_cube_solver.enums.Direction import Direction
from rubik_cube_solver.enums.Layer import Layer

def main():
    # Create a Rubik's Cube
    cube = Cube(3)
    rotator = Rotator(cube)

    # U R' L2 F U2 B' D L' R2 F' U B2 D' L R' F2 U' B D2 L'

    # Sequence of 20 moves
    moves = [
        Move(Layer.UP, Direction.CW, 1),
        Move(Layer.RIGHT, Direction.CCW, 1),
        Move(Layer.LEFT, Direction.DOUBLE, 1),
        Move(Layer.FRONT, Direction.CW, 1),
        Move(Layer.UP, Direction.DOUBLE, 1),
        Move(Layer.BACK, Direction.CCW, 1),
        Move(Layer.DOWN, Direction.CW, 1),
        Move(Layer.LEFT, Direction.CCW, 1),
        Move(Layer.RIGHT, Direction.DOUBLE, 1),
        Move(Layer.FRONT, Direction.CCW, 1),
        Move(Layer.UP, Direction.CW, 1),
        Move(Layer.BACK, Direction.DOUBLE, 1),
        Move(Layer.DOWN, Direction.CCW, 1),
        Move(Layer.LEFT, Direction.CW, 1),
        Move(Layer.RIGHT, Direction.CCW, 1),
        Move(Layer.FRONT, Direction.DOUBLE, 1),
        Move(Layer.UP, Direction.CCW, 1),
        Move(Layer.BACK, Direction.CW, 1),
        Move(Layer.DOWN, Direction.DOUBLE, 1),
        Move(Layer.LEFT, Direction.CCW, 1),
    ]

    # Apply the moves
    for move in moves:
        rotator.turn(move)

    print(cube)

    rotation = Rotation.Z
    rotator.rotate(rotation, -1)

    # Print final cube state
    print("Final cube state:")
    print(cube)


if __name__ == "__main__":
    main()
