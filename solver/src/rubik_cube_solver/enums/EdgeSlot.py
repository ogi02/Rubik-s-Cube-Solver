# Python imports
from enum import Enum
from typing import Self


class EdgeSlot(Enum):
    UF = "UF"
    UB = "UB"
    UL = "UL"
    UR = "UR"
    DF = "DF"
    DB = "DB"
    DL = "DL"
    DR = "DR"
    FL = "FL"
    FR = "FR"
    BL = "BL"
    BR = "BR"

    @classmethod
    def from_value(cls, value: str) -> Self:
        """
        Return an enumeration value from string.

        :param value: The string value
        :return: The enumeration value
        """

        match value:
            case "UF":
                return EdgeSlot.UF
            case "UB":
                return EdgeSlot.UB
            case "UL":
                return EdgeSlot.UL
            case "UR":
                return EdgeSlot.UR
            case "DF":
                return EdgeSlot.DF
            case "DB":
                return EdgeSlot.DB
            case "DL":
                return EdgeSlot.DL
            case "DR":
                return EdgeSlot.DR
            case "FL":
                return EdgeSlot.FL
            case "FR":
                return EdgeSlot.FR
            case "BL":
                return EdgeSlot.BL
            case "BR":
                return EdgeSlot.BR
            case _:
                raise ValueError(f"Invalid value {value} for the EdgeSlot enumeration")
