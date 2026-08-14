# Python imports
from enum import Enum
from typing import Self


class Direction(Enum):
    CW = ""
    CCW = "'"
    DOUBLE = "2"

    @classmethod
    def from_value(cls, value: str) -> Self:
        """
        Return an enumeration value from string.

        :param value: The string value
        :return: The enumeration value
        """

        match value:
            case "":
                return Direction.CW
            case "'":
                return Direction.CCW
            case "2":
                return Direction.DOUBLE
            case _:
                raise ValueError(f"Invalid value {value} for the Direction enumeration")
