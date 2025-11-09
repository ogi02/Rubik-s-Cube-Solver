# Python imports
from enum import Enum


class Role(Enum):
    """
    Enum representing different user roles in the system.
    """

    SOLVER = "SOLVER"
    VISUALIZER = "VISUALIZER"

    @staticmethod
    def from_str(label: str) -> "Role":
        """
        Convert a string to a Role enum member.

        :param label: The string representation of the role.
        :return: The corresponding Role enum member.
        :raise ValueError: If the label does not correspond to any Role.
        """
        match label.upper():
            case "SOLVER":
                return Role.SOLVER
            case "VISUALIZER":
                return Role.VISUALIZER
            case _:
                raise ValueError(f"Unknown role: {label}")
