# Python imports
from enum import Enum
from typing import Self


class Layer(Enum):
    UP = "U"
    DOWN = "D"
    LEFT = "L"
    RIGHT = "R"
    FRONT = "F"
    BACK = "B"

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
