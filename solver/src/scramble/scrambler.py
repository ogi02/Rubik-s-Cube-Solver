import random

from cube_rotation.move import Move
from enums.Direction import Direction
from enums.Layer import Layer


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

    def generate_scramble(self, cube_size: int, scramble_length: int | None = None) -> list[Move]:
        """
        Generates a scramble for a cube of given size.

        :param cube_size: Size of the cube (e.g., 2 for 2x2, 3 for 3x3, etc.)
        :param scramble_length: Length of the scramble (optional)
        :return: List of moves in the scramble
        """

        match cube_size:
            case 2:
                return self.__generate_scramble_2x2(scramble_length or 8)
            case 3:
                return self.__generate_scramble_3x3(scramble_length or 20)
            case _:
                return self.__generate_scramble_nxn(cube_size, scramble_length or (cube_size - 2) * 20)

    @staticmethod
    def is_valid_random_move(move: Move, previous_moves: list[Move]) -> bool:
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

    def should_append_to_previous_moves(self, move: Move, previous_moves: list[Move]) -> bool:
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

    def __generate_scramble_2x2(self, scramble_length: int) -> list[Move]:
        """
        Generates a scramble for a 2x2 cube.

        :param scramble_length: Length of the scramble
        :return: List of moves in the scramble
        """

        faces = [Layer.UP, Layer.FRONT, Layer.RIGHT]

        scramble: list[Move] = []
        previous_faces: list[Move] = []

        while len(scramble) < scramble_length:
            # Choose a random face
            face = random.choice([f for f in faces])

            # Choose a random direction
            direction = random.choice(self.directions)

            # Create the move
            move = Move(layer=face, direction=direction, layer_amount=1)

            # If the move or its opposite is already in the previous faces, skip
            if not self.is_valid_random_move(move, previous_faces):
                continue

            # If a different move on the same axis is picked, append
            if self.should_append_to_previous_moves(move, previous_faces):
                previous_faces.append(move)
            # If any other face is picked, reset the previous_face list
            else:
                previous_faces = [move]

            # Append the move to the scramble
            scramble.append(move)

        return scramble

    def __generate_scramble_3x3(self, scramble_length: int) -> list[Move]:
        """
        Generates a scramble for a 3x3 cube.

        :param scramble_length: Length of the scramble
        :return: List of moves in the scramble
        """

        scramble: list[Move] = []
        previous_faces: list[Move] = []

        while len(scramble) < scramble_length:
            # Choose a random face
            face = random.choice([f for f in self.faces])

            # Choose a random direction
            direction = random.choice(self.directions)

            # Create the move
            move = Move(layer=face, direction=direction, layer_amount=1)

            # If the move or its opposite is already in the previous faces, skip
            if not self.is_valid_random_move(move, previous_faces):
                continue

            # If a different move on the same axis is picked, append
            if self.should_append_to_previous_moves(move, previous_faces):
                previous_faces.append(move)
            # If any other face is picked, reset the previous_face list
            else:
                previous_faces = [move]

            # Append the move to the scramble
            scramble.append(move)

        return scramble

    def __generate_scramble_nxn(self, cube_size: int, scramble_length: int) -> list[Move]:
        """
        Generates a scramble for an NxN cube.

        :param cube_size: Size of the cube
        :param scramble_length: Length of the scramble
        :return: List of moves in the scramble
        """

        scramble: list[Move] = []
        previous_faces: list[Move] = []

        while len(scramble) < scramble_length:
            # Choose a random face
            face = random.choice([f for f in self.faces])

            # Choose a random direction
            direction = random.choice(self.directions)

            # Choose a random layer amount
            layer_amount = random.randint(1, cube_size // 2)

            # Create the move
            move = Move(layer=face, direction=direction, layer_amount=layer_amount)

            # If the move or its opposite is already in the previous faces, skip
            if not self.is_valid_random_move(move, previous_faces):
                continue

            # If a different move on the same axis is picked, append
            if self.should_append_to_previous_moves(move, previous_faces):
                previous_faces.append(move)
            # If any other face is picked, reset the previous_face list
            else:
                previous_faces = [move]

            # Append the move to the scramble
            scramble.append(move)

        return scramble
