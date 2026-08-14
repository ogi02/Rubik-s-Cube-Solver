# Python imports
import re
from typing import Self

# Project imports
from rubik_cube_solver.enums.Direction import Direction
from rubik_cube_solver.enums.Layer import Layer


class Move:
    """
    Represents a single move on a Rubik's Cube.
    """

    def __init__(self, layer: Layer, direction: Direction, layer_amount: int):
        """
        Constructor for the `Move` class.

        :param layer: The layer to rotate
        :param direction: The direction to rotate
        :param layer_amount: The amount of layers to rotate
        """

        self.__layer = layer
        self.__direction = direction
        self.__layer_amount = layer_amount

    @property
    def layer(self) -> Layer:
        """
        Layer getter.

        :return: The layer
        """

        return self.__layer

    @layer.setter
    def layer(self, layer: Layer):
        """
        Layer setter.

        :param layer: The layer
        :return: None
        """

        self.__layer = layer

    @property
    def direction(self) -> Direction:
        """
        Direction getter.

        :return: The direction
        """

        return self.__direction

    @direction.setter
    def direction(self, direction: Direction):
        """
        Direction setter.

        :param direction: The direction
        :return: None
        """

        self.__direction = direction

    @property
    def layer_amount(self) -> int:
        """
        Layer amount getter.

        :return: The layer amount
        """

        return self.__layer_amount

    @layer_amount.setter
    def layer_amount(self, layer_amount: int):
        """
        Layer amount setter.

        :param layer_amount: The layer amount
        :return: None
        """

        self.__layer_amount = layer_amount

    def __str__(self) -> str:
        """
        String representation of the Move.

        :return: String representation
        """

        match self.__layer_amount:
            case 1:
                return f"{self.__layer.value}{self.__direction.value}"
            case 2:
                return f"{self.__layer.value}w{self.__direction.value}"
            case _:
                return f"{self.__layer_amount}{self.__layer.value}w{self.__direction.value}"

    def __eq__(self, other) -> bool:
        """
        Equality comparison for Move objects.

        :param other: The other Move object to compare with
        :return: True if equal, False otherwise
        """

        if not isinstance(other, Move):
            return False

        return (
            self.layer == other.layer and self.direction == other.direction and self.layer_amount == other.layer_amount
        )

    @classmethod
    def from_str(cls, move_string: str) -> Self:
        r"""
        Create a Move from string.

        Regex pattern explanation:
        Group 1 - Layer Amount - (\d+)? - Optional number prefix
        Group 2 - Layer - ([UDLRFB]) - One of the faces
        Group 3 - Wide Move - (w?) - Optional "w" indicating a wide move
        Group 4 - Direction - (['2]?) - Optional one of "'" (CCW) or "2" (Double)

        :param move_string: The string representation of a move
        :return: A new Move object
        """

        pattern = r"^(\d+)?([UDLRFB])(w?)(['2]?)$"
        match = re.match(pattern, move_string.strip())
        if not match:
            raise ValueError(f"Couldn't parse move notation: {move_string}")

        layer_amount_group, layer_group, wide_group, direction_group = match.groups()

        layer = Layer.from_value(layer_group)
        direction = Direction.from_value(direction_group)

        if layer_amount_group:
            layer_amount = int(layer_amount_group)
            if layer_amount < 2 or not wide_group:
                raise ValueError(f"Couldn't parse move notation: {move_string}")
        elif wide_group:
            layer_amount = 2
        else:
            layer_amount = 1

        return cls(layer, direction, layer_amount)
