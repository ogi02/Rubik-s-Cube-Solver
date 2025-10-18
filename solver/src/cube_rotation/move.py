from enums.Direction import Direction
from enums.Layer import Layer


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

        return (
            self.layer == other.layer and self.direction == other.direction and self.layer_amount == other.layer_amount
        )
