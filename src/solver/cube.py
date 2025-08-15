from src.solver.enums.Color import Color
from src.solver.enums.Direction import Direction
from src.solver.enums.Layer import Layer


class Cube:
    def __init__(self):
        # Initialize the cube with a solved state
        self.layers = {
            Layer.UP: [Color.WHITE] * 9,
            Layer.DOWN: [Color.YELLOW] * 9,
            Layer.LEFT: [Color.ORANGE] * 9,
            Layer.RIGHT: [Color.RED] * 9,
            Layer.FRONT: [Color.GREEN] * 9,
            Layer.BACK: [Color.BLUE] * 9
        }
        self.cube_size = 3

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
            start = row * self.cube_size
            end = start + self.cube_size
            return " ".join(f.value for f in face[start:end])

        # Dynamic padding to UP and DOWN layers
        pad = " " * (self.cube_size * 2)

        string_representation = ""

        # Add UP layer
        for row in range(self.cube_size):
            string_representation += f"{pad}{row_str(self.layers[Layer.UP], row)}\n"
        # Add LEFT, FRONT, RIGHT and BACK layers
        for row in range(self.cube_size):
            string_representation += (f"{row_str(self.layers[Layer.LEFT], row)} "
                                      f"{row_str(self.layers[Layer.FRONT], row)} "
                                      f"{row_str(self.layers[Layer.RIGHT], row)} "
                                      f"{row_str(self.layers[Layer.BACK], row)}\n")
        # Add DOWN layer
        for row in range(self.cube_size):
            string_representation += f"{pad}{row_str(self.layers[Layer.DOWN], row)}\n"

        return string_representation

    def rotate(self, layer: Layer, layer_amount: int, direction: Direction):
        """
        Rotates a given amount of layers in the given direction.
        Acts as a wrapper method for rotating the face and the sides of a layer
        Possible faces: 'U', 'D', 'L', 'R', 'F', 'B'.
        Possible directions: clockwise, counter-clockwise, double

        :param layer: The layer to rotate
        :param layer_amount: The amount of layers to rotate
        :param direction: The direction to rotate
        :return: None
        """
        pass

    def scramble(self):
        # Implement scramble logic
        pass

    def solve(self):
        # Implement solve logic using CFOP
        pass

if __name__ == '__main__':
    cube = Cube()
    print(cube)

