# Python imports
from enum import Enum


class Direction(Enum):
    CW = ""
    CCW = "'"
    DOUBLE = "2"

    def inverse(self) -> "Direction":
        """
        Return the direction that undoes this one.

        A double turn undoes itself, so it is its own inverse.

        :return: The opposite direction
        """

        match self:
            case Direction.CW:
                return Direction.CCW
            case Direction.CCW:
                return Direction.CW
            case _:
                return Direction.DOUBLE

    @classmethod
    def from_value(cls, value: str) -> "Direction":
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
