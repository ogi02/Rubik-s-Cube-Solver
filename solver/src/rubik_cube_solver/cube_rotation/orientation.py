# Python imports
from collections import deque
from typing import Self

# Project imports
from rubik_cube_solver.cube_rotation.cube_rotation import MOVE_TRANSLATION_MAP
from rubik_cube_solver.cube_rotation.move import Move
from rubik_cube_solver.enums.Direction import Direction
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.enums.Rotation import Rotation


class Orientation:
    """
    Represents the way a cube is held, as the layer that every face name refers to.

    A cube held as it was built is the identity orientation, where every name refers to its own
    layer. Each whole-cube rotation moves the faces around, so the same name then refers to a
    different layer, and there are twenty-four orientations in total.
    """

    def __init__(self, layers: dict[Layer, Layer] | None = None) -> None:
        """
        Constructor for the `Orientation` class.

        :param layers: The layer every face name refers to, or None for a cube held as it was built
        :return: None
        """

        self.__layers = layers if layers is not None else {layer: layer for layer in Layer}

    @property
    def layers(self) -> dict[Layer, Layer]:
        """
        Layers getter.

        :return: The layer every face name refers to
        """

        return self.__layers

    def __eq__(self, other) -> bool:
        """
        Equality comparison for Orientation objects.

        :param other: The other Orientation object to compare with
        :return: True if equal, False otherwise
        """

        if not isinstance(other, Orientation):
            return False

        return self.__layers == other.layers

    def __hash__(self) -> int:
        """
        Hash of the orientation, so it can be used as a dictionary key.

        :return: The hash
        """

        return hash(tuple(self.__layers.items()))

    def rotate(self, rotation: Move) -> "Orientation":
        """
        Return the orientation the cube is held in after a whole-cube rotation.

        The rotation sends the face at every position to a new one, so a name written after it
        refers to the layer that used to sit at the position the name now points at. This
        orientation is left untouched.

        Example: rotating the identity orientation by `x` makes `UP` refer to `FRONT`.

        :param rotation: The whole-cube rotation to perform
        :return: The orientation after the rotation
        """

        translation = MOVE_TRANSLATION_MAP[(rotation.layer, rotation.direction)]

        return Orientation({layer: self.__layers[translation[layer]] for layer in Layer})

    def to_moves(self) -> list[Move]:
        """
        Return the shortest sequence of whole-cube rotations that holds a cube this way.

        Every orientation is reached from the identity one by a breadth-first walk over the nine
        rotations, so the first sequence that arrives at this orientation is a shortest one. No
        orientation needs more than two rotations.

        Example: the orientation of `x` followed by `x` is written as `x2`.

        :return: The shortest sequence of whole-cube rotations
        """

        sequences: dict[Orientation, list[Move]] = {Orientation(): []}
        queue: deque[Orientation] = deque(sequences)

        while queue:
            orientation = queue.popleft()
            for rotation in Rotation:
                for direction in Direction:
                    move = Move(rotation, direction, 1)
                    rotated = orientation.rotate(move)
                    if rotated not in sequences:
                        sequences[rotated] = sequences[orientation] + [move]
                        queue.append(rotated)

        return sequences[self]

    @classmethod
    def from_moves(cls, rotations: list[Move]) -> Self:
        """
        Create an Orientation from a sequence of whole-cube rotations.

        The rotations are performed in order on a cube held as it was built.

        :param rotations: The whole-cube rotations to perform
        :return: A new Orientation object
        """

        orientation = cls()
        for rotation in rotations:
            orientation = orientation.rotate(rotation)

        return orientation
