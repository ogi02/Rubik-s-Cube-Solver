# Python imports
from enum import Enum
from typing import Self

# Project imports
from rubik_cube_solver.enums.Rotation import Rotation


class Layer(Enum):
    UP = "U"
    DOWN = "D"
    LEFT = "L"
    RIGHT = "R"
    FRONT = "F"
    BACK = "B"

    def opposite(self) -> "Layer":
        """
        Return the face on the other side of the cube.

        :return: The opposite face
        """

        match self:
            case Layer.UP:
                return Layer.DOWN
            case Layer.DOWN:
                return Layer.UP
            case Layer.LEFT:
                return Layer.RIGHT
            case Layer.RIGHT:
                return Layer.LEFT
            case Layer.FRONT:
                return Layer.BACK
            case _:
                return Layer.FRONT

    def axis(self) -> Rotation:
        """
        Return the axis of the whole-cube rotation that turns about the same axis as the face.

        `x` turns like RIGHT, `y` like UP and `z` like FRONT; their opposite faces turn the other way
        about the same axis.

        :return: The rotation axis
        """

        match self:
            case Layer.RIGHT | Layer.LEFT:
                return Rotation.X
            case Layer.UP | Layer.DOWN:
                return Rotation.Y
            case _:
                return Rotation.Z

    def turns_with_axis(self) -> bool:
        """
        Return whether a clockwise turn of the face turns the same way as its axis's rotation.

        That is RIGHT, UP and FRONT; LEFT, DOWN and BACK turn clockwise the other way.

        :return: Whether the face turns with its axis
        """

        return self in (Layer.RIGHT, Layer.UP, Layer.FRONT)

    @classmethod
    def from_value(cls, value: str) -> Self:
        """
        Return an enumeration value from string.

        :param value: The string value
        :return: The enumeration value
        """

        match value:
            case "U":
                return Layer.UP
            case "D":
                return Layer.DOWN
            case "L":
                return Layer.LEFT
            case "R":
                return Layer.RIGHT
            case "F":
                return Layer.FRONT
            case "B":
                return Layer.BACK
            case _:
                raise ValueError(f"Invalid value {value} for the Layer enumeration")
