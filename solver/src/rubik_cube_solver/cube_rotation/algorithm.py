# Python imports
from typing import Self

# Project imports
from rubik_cube_solver.cube_rotation.cube_rotation import MOVE_TRANSLATION_MAP
from rubik_cube_solver.cube_rotation.move import Move
from rubik_cube_solver.cube_rotation.move_cancellation import can_combine, combine
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.enums.Rotation import Rotation


class Algorithm:
    """
    Represents an algorithm (a sequence of moves that can be performed on a Rubik's Cube).
    """

    def __init__(self, moves: list[Move]) -> None:
        """
        Constructor for the `Algorithm` class.

        :param moves: The moves of the algorithm
        :return: None
        """

        self.__moves = moves

    @property
    def moves(self) -> list[Move]:
        """
        Moves getter.

        :return: The moves
        """

        return self.__moves

    @moves.setter
    def moves(self, moves: list[Move]) -> None:
        """
        Moves setter.

        :param moves: The moves
        :return: None
        """

        self.__moves = moves

    def __str__(self) -> str:
        """
        String representation of the algorithm.

        :return: String representation
        """

        return " ".join(str(move) for move in self.__moves)

    def __eq__(self, other) -> bool:
        """
        Equality comparison for Algorithm objects.

        :param other: The other Algorithm object to compare with
        :return: True if equal, False otherwise
        """

        if not isinstance(other, Algorithm):
            return False

        return self.moves == other.moves

    def remove_rotations(self) -> None:
        """
        Removes all whole-cube rotations from the algorithm.

        A rotation does not turn any layer, it only changes which face every following move refers to.
        Every rotation is therefore dropped and each move after it is rewritten in the orientation the
        cube had before the rotation, which leaves an equivalent algorithm of layer turns only.

        Example: `x R U R' U'` becomes `R F R' F'`.

        :return: None
        """

        # The layer each move names, expressed in the orientation the algorithm started from
        orientation: dict[Layer, Layer] = {layer: layer for layer in Layer}
        moves: list[Move] = []

        for move in self.__moves:
            if isinstance(move.layer, Rotation):
                translation = MOVE_TRANSLATION_MAP[(move.layer, move.direction)]
                orientation = {layer: orientation[translation[layer]] for layer in Layer}
            else:
                moves.append(Move(orientation[move.layer], move.direction, move.layer_amount))

        self.__moves = moves

    def cancel_moves(self) -> None:
        """
        Reduces the algorithm by cancelling and combining adjacent moves that name the same
        layer (or rotation axis) and, for layer turns, the same layer amount.

        Cancellation cascades: once a pair of moves disappears or combines into one, the moves
        that become newly adjacent are considered as well.

        Example: `R U U' R2` becomes `R'`.

        :return: None
        """

        moves: list[Move] = []

        for move in self.__moves:
            current: Move | None = move
            while moves and current is not None and can_combine(moves[-1], current):
                current = combine(moves.pop(), current)
            if current is not None:
                moves.append(current)

        self.__moves = moves

    def merge(self, other: "Algorithm") -> None:
        """
        Merges another algorithm into this one, then cancels moves across the whole result.

        `other` is left untouched; the concatenated and cancelled moves are stored on this
        algorithm.

        Example: `R U U' R2` merged with `L` becomes `R' L`.

        :param other: The algorithm to merge into this one
        :return: None
        """

        self.__moves = self.__moves + other.moves
        self.cancel_moves()

    @classmethod
    def from_str(cls, algorithm_string: str) -> Self:
        """
        Create an Algorithm from string.

        Moves are separated by any amount of whitespace. An empty or whitespace-only string
        produces an algorithm with no moves.

        :param algorithm_string: The string representation of an algorithm
        :return: A new Algorithm object
        """

        return cls([Move.from_str(move_string) for move_string in algorithm_string.split()])
