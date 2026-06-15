# Python imports
from enum import Enum


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
