# Python imports
from enum import Enum
from typing import Self


class CornerSlot(Enum):
    UFL = "UFL"
    UFR = "UFR"
    UBL = "UBL"
    UBR = "UBR"
    DFL = "DFL"
    DFR = "DFR"
    DBL = "DBL"
    DBR = "DBR"

    @classmethod
    def from_value(cls, value: str) -> Self:
        """
        Return an enumeration value from string.

        :param value: The string value
        :return: The enumeration value
        """

        match value:
            case "UFL":
                return CornerSlot.UFL
            case "UFR":
                return CornerSlot.UFR
            case "UBL":
                return CornerSlot.UBL
            case "UBR":
                return CornerSlot.UBR
            case "DFL":
                return CornerSlot.DFL
            case "DFR":
                return CornerSlot.DFR
            case "DBL":
                return CornerSlot.DBL
            case "DBR":
                return CornerSlot.DBR
            case _:
                raise ValueError(f"Invalid value {value} for the CornerSlot enumeration")
