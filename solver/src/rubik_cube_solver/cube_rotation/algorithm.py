# Python imports
from typing import Self

# Project imports
from rubik_cube_solver.cube_rotation.move import Move
from rubik_cube_solver.cube_rotation.move_cancellation import can_combine, combine
from rubik_cube_solver.cube_rotation.orientation import Orientation
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

    def inverse(self) -> "Algorithm":
        """
        Return the algorithm that undoes this one.

        Every move is inverted and the order is reversed, so the last move performed is the first
        one taken back. This algorithm is left untouched.

        Example: `R U R'` becomes `R U' R'`.

        :return: The inverse algorithm
        """

        return Algorithm([move.inverse() for move in reversed(self.__moves)])

    def remove_rotations(self) -> None:
        """
        Removes all whole-cube rotations from the algorithm.

        A rotation does not turn any layer, it only changes which face every following move refers to.
        Every rotation is therefore dropped and each move after it is rewritten in the orientation the
        cube had before the rotation, which leaves an equivalent algorithm of layer turns only.

        Example: `x R U R' U'` becomes `R F R' F'`.

        :return: None
        """

        # The way the cube is held, expressed in the orientation the algorithm started from
        orientation = Orientation()
        moves: list[Move] = []

        for move in self.__moves:
            if isinstance(move.layer, Rotation):
                orientation = orientation.rotate(move)
            else:
                moves.append(Move(orientation.layers[move.layer], move.direction, move.layer_amount))

        self.__moves = moves

    def rename(self, grip: "Algorithm") -> None:
        """
        Renames every move to the face it is called by once the cube is held in the given grip.

        The algorithm then turns exactly the same pieces of the same cube as before, provided the
        grip's rotations are performed first: only the name each layer goes by has changed, because
        the cube has been turned. Performing the grip, this algorithm and then the grip's inverse
        therefore does the very same work, on a face the grip has brought into view, and
        `remove_rotations` over the three takes them straight back to what they were.

        Example: `L U L'` renamed for the grip `y'` becomes `F U F'`, since a cube turned by `y'`
        calls its left face the front one.

        :param grip: The whole-cube rotations the cube is held in
        :return: None
        """

        names = Orientation.from_moves(grip.moves).inverse().layers
        moves: list[Move] = []

        for move in self.__moves:
            if isinstance(move.layer, Rotation):
                face = names[Layer.from_axis(move.layer)]
                direction = move.direction if face.turns_with_axis() else move.direction.inverse()
                moves.append(Move(face.axis(), direction, move.layer_amount))
            else:
                moves.append(Move(names[move.layer], move.direction, move.layer_amount))

        self.__moves = moves

    def shorten_rotations(self) -> None:
        """
        Replaces every run of adjacent whole-cube rotations with the shortest sequence that holds
        the cube the same way.

        The layer turns are left exactly where they are, so the algorithm keeps turning the cube
        the way it was written; only the rotations between them are rewritten, and a run that
        holds the cube the way it already was disappears.

        Example: `R x x L z z' U` becomes `R x2 L U`.

        :return: None
        """

        moves: list[Move] = []
        rotations: list[Move] = []

        for move in self.__moves:
            if isinstance(move.layer, Rotation):
                rotations.append(move)
                continue

            if rotations:
                moves += Orientation.from_moves(rotations).to_moves()
                rotations = []

            moves.append(move)

        if rotations:
            moves += Orientation.from_moves(rotations).to_moves()

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
