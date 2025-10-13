from src.solver.cube import Cube
from src.solver.cube_rotation.face_stickers_rotation import rotate_face
from src.solver.cube_rotation.side_stickers_rotation import rotate_sides
from src.solver.enums.Direction import Direction
from src.solver.enums.Layer import Layer


class Rotator:
    """
    The `Rotator` class is responsible for all turns done on the cube.
    It holds a reference of the cube and performs all turns.
    """

    def __init__(self, cube: Cube):
        """
        Constructor for the `Rotator` class.

        :param cube: The cube
        """
        self.__cube = cube

    @property
    def cube(self) -> Cube:
        """
        Cube getter

        :return: The cube
        """
        return self.__cube

    @cube.setter
    def cube(self, cube: Cube):
        """
        Cube setter

        :param cube: The cube
        :return: None
        """
        self.__cube = cube

    def turn(self, layer: Layer, layer_amount: int, direction: Direction) -> None:
        """
        Turns a layer or multiple layers of the cube.
        Firstly, it generates a map for the rotation of the face stickers and performs the rotation.
        Secondly, for every layer in `layer_amount` it moves around the sides stickers, depending on the adjacent faces.

        Possible faces: 'U', 'D', 'L', 'R', 'F', 'B'.
        Possible directions: clockwise, counter-clockwise, double

        :param layer: The layer to rotate
        :param layer_amount: The amount of layers to rotate
        :param direction: The direction to rotate
        :return: None
        """

        # Rotate the face stickers
        rotate_face(self.__cube, layer, direction)

        # Rotate the side stickers
        rotate_sides(self.__cube, layer, direction, layer_amount)
