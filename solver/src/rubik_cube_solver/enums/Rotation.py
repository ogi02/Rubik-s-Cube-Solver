# Python imports
from enum import Enum
from typing import Self


class Rotation(Enum):
    """
    Enum representing the axes of whole-cube rotations.

    Each value corresponds to a standard Rubik's Cube rotation axis:
    - X: rotation around the x-axis (same direction as an R move)
    - Y: rotation around the y-axis (same direction as a U move)
    - Z: rotation around the z-axis (same direction as an F move)
    """

    X = "x"
    Y = "y"
    Z = "z"

    @classmethod
    def from_value(cls, value: str) -> Self:
        """
        Return an enumeration value from string.

        :param value: The string value
        :return: The enumeration value
        """

        match value:
            case "x":
                return Rotation.X
            case "y":
                return Rotation.Y
            case "z":
                return Rotation.Z
            case _:
                raise ValueError(f"Invalid value {value} for the Rotation enumeration")
