import random

from rubik_cube_solver.cube_rotation.move import Move
from rubik_cube_solver.enums.Direction import Direction
from rubik_cube_solver.enums.Layer import Layer


class Scrambler:
    """
    Scrambler class that can generate scrambles for different cubes.
    """

    def __init__(self):
        """
        Initializes the Scrambler class.
        """
        self.faces = [Layer.UP, Layer.DOWN, Layer.FRONT, Layer.BACK, Layer.LEFT, Layer.RIGHT]
        self.directions = [Direction.CW, Direction.CCW, Direction.DOUBLE]

        self.opposite_faces = {
            Layer.UP: Layer.DOWN,
            Layer.DOWN: Layer.UP,
            Layer.FRONT: Layer.BACK,
            Layer.BACK: Layer.FRONT,
            Layer.LEFT: Layer.RIGHT,
            Layer.RIGHT: Layer.LEFT,
        }

    def generate_scramble(self, cube_size: int) -> list[Move]:
        """
        Generates a scramble for a cube of given size.

        :param cube_size: Size of the cube (e.g., 2 for 2x2, 3 for 3x3, etc.)
        :return: List of moves in the scramble
        """

        if cube_size < 2:
            raise ValueError("Cube size must be at least 2.")

        # Determine scramble length
        scramble_length = self._get_scramble_length(cube_size)

        scramble: list[Move] = []
        previous_faces: list[Move] = []
        # Generate scramble
        while len(scramble) < scramble_length:
            # Create a random move
            move = self._generate_random_move(cube_size)

            # If the move or its opposite is already in the previous faces, skip
            if not self._is_valid_random_move(move, previous_faces):
                continue

            # If a different move on the same axis is picked, append
            if self._should_append_to_previous_moves(move, previous_faces):
                previous_faces.append(move)
            # If any other face is picked, reset the previous_face list
            else:
                previous_faces = [move]

            # Append the move to the scramble
            scramble.append(move)

        return scramble

    @staticmethod
    def _get_scramble_length(cube_size: int) -> int:
        """
        Determines the default scramble length based on cube size.

        :param cube_size: Size of the cube
        :return: Default scramble length
        """

        if cube_size < 2:
            raise ValueError("Cube size must be at least 2.")

        match cube_size:
            case 2:
                return 8
            case 3:
                return 20
            case _:
                return (cube_size - 2) * 20

    def _generate_random_move(self, cube_size: int) -> Move:
        """
        Generates a random move for a cube of given size.

        :param cube_size: Size of the cube
        :return: A randomly generated move
        """

        if cube_size < 2:
            raise ValueError("Cube size must be at least 2.")

        # If the cube is 2x2, use only UP, FRONT, RIGHT faces
        if cube_size == 2:
            face = random.choice([Layer.UP, Layer.FRONT, Layer.RIGHT])
        # Choose a random face
        else:
            face = random.choice([f for f in self.faces])

        # Choose a random direction
        direction = random.choice(self.directions)

        # If the cube is 2x2 or 3x3, layer amount is always 1
        if cube_size == 2 or cube_size == 3:
            layer_amount = 1
        # Choose a random layer amount
        else:
            layer_amount = random.randint(1, cube_size // 2)

        return Move(layer=face, direction=direction, layer_amount=layer_amount)

    @staticmethod
    def _is_valid_random_move(move: Move, previous_moves: list[Move]) -> bool:
        """
        Checks if a randomly generated move is valid based on the previous move.

        :param move: The current move to check
        :param previous_moves: The previous move made
        :return: True if the move is valid, False otherwise
        """

        if not previous_moves:
            return True
        for prev_move in previous_moves:
            # If the move is on the same layer and has the same layer amount as the previous move, it's invalid
            if move.layer == prev_move.layer and move.layer_amount == prev_move.layer_amount:
                return False
        return True

    def _should_append_to_previous_moves(self, move: Move, previous_moves: list[Move]) -> bool:
        """
        Determines if the current move should be appended to the list of previous moves.

        :param move: The current move to check
        :param previous_moves: The previous moves made
        :return: True if the move should be appended, False otherwise
        """

        if not previous_moves:
            return False
        # If the move is on the same or opposite layer as the moves in the previous_moves list
        if move.layer == previous_moves[0].layer or move.layer == self.opposite_faces.get(previous_moves[0].layer):
            return True
        return False
