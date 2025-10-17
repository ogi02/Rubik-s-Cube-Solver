from solver.enums.Color import Color
from solver.enums.Layer import Layer

class Cube:
    def __init__(self, size: int):
        # Initialize the cube with a solved state
        self.__layers = {
            Layer.UP: [Color.WHITE] * size * size,
            Layer.DOWN: [Color.YELLOW] * size * size,
            Layer.LEFT: [Color.ORANGE] * size * size,
            Layer.RIGHT: [Color.RED] * size * size,
            Layer.FRONT: [Color.GREEN] * size * size,
            Layer.BACK: [Color.BLUE] * size * size
        }
        self.__size = size

    @property
    def size(self) -> int:
        """
        Cube size getter

        :return: The cube size
        """
        return self.__size

    @size.setter
    def size(self, cube_size: int) -> None:
        """
        Cube size setter

        :param cube_size: The cube size
        """
        self.__size = cube_size

    @property
    def layers(self) -> dict[Layer, list[Color]]:
        """
        Layers getter

        :return: The layers of the cube
        """
        return self.__layers

    @layers.setter
    def layers(self, layers: dict[Layer, list[Color]]) -> None:
        """
        Layers setter

        :param layers: The layers of the cube
        """
        self.__layers = layers


    def __str__(self):
        """
        Return a string representation of the Cube in the following format:

               U U U
               U U U
               U U U
        L L L  F F F  R R R  B B B
        L L L  F F F  R R R  B B B
        L L L  F F F  R R R  B B B
               D D D
               D D D
               D D D

        :return: The string representation of the Cube
        """

        def row_str(face: list[Color], r: int) -> str:
            """
            Returns a string for one row of a face.

            :param face: The face to be printed.
            :param r: The row to be printed.
            :return: The string representation of the row
            """
            start = r * self.size
            end = start + self.size
            return " ".join(f.value for f in face[start:end])

        # Dynamic padding to UP and DOWN layers
        pad = " " * (self.size * 2)

        string_representation = ""

        # Add UP layer
        for row in range(self.size):
            string_representation += f"{pad}{row_str(self.layers[Layer.UP], row)}\n"
        # Add LEFT, FRONT, RIGHT and BACK layers
        for row in range(self.size):
            string_representation += (f"{row_str(self.layers[Layer.LEFT], row)} "
                                      f"{row_str(self.layers[Layer.FRONT], row)} "
                                      f"{row_str(self.layers[Layer.RIGHT], row)} "
                                      f"{row_str(self.layers[Layer.BACK], row)}\n")
        # Add DOWN layer
        for row in range(self.size):
            string_representation += f"{pad}{row_str(self.layers[Layer.DOWN], row)}\n"

        return string_representation

    def scramble(self):
        # Implement scramble logic
        pass

    def solve(self):
        # Implement solve logic using CFOP
        pass
