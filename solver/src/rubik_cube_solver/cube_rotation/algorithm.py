# Python imports
from typing import Self

# Project imports
from rubik_cube_solver.cube_rotation.move import Move


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
