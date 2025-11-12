from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.face_stickers_rotation import rotate_face
from rubik_cube_solver.cube_rotation.move import Move
from rubik_cube_solver.cube_rotation.side_stickers_rotation import rotate_sides


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

    def turn(self, move: Move) -> None:
        """
        Turns a layer or multiple layers of the cube.
        Firstly, it generates a map for the rotation of the face stickers and performs the rotation.
        Secondly, for every layer in `layer_amount` it moves around the sides stickers, depending on the adjacent faces.

        Possible faces: 'U', 'D', 'L', 'R', 'F', 'B'.
        Possible directions: clockwise, counter-clockwise, double

        :param move: The move to perform
        :return: None
        """

        # Rotate the face stickers
        rotate_face(self.__cube, move.layer, move.direction)

        # Rotate the side stickers
        rotate_sides(self.__cube, move.layer, move.direction, move.layer_amount)
