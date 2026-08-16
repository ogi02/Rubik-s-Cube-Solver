# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.cube_rotation.cube_rotation import CUBE_ROTATION_MAP
from rubik_cube_solver.cube_rotation.face_stickers_rotation import rotate_face
from rubik_cube_solver.cube_rotation.move import Move
from rubik_cube_solver.cube_rotation.side_stickers_rotation import rotate_sides
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.Direction import Direction
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.enums.Rotation import Rotation


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

        A move carrying a whole-cube rotation instead of a layer is forwarded to `rotate`.

        Possible faces: 'U', 'D', 'L', 'R', 'F', 'B'.
        Possible directions: clockwise, counter-clockwise, double

        :param move: The move to perform
        :return: None
        """

        # Forward whole-cube rotations
        if isinstance(move.layer, Rotation):
            self.rotate(move.layer, move.direction)
            return

        # Rotate the face stickers
        rotate_face(self.__cube, move.layer, move.direction)

        # Rotate the side stickers
        rotate_sides(self.__cube, move.layer, move.direction, move.layer_amount)

    def rotate(self, rotation: Rotation, direction: Direction) -> None:
        """
        Applies a whole-cube rotation around the specified axis.

        The rotation remaps all 6 faces of the cube according to the axis
        and also rotates the stickers of the two faces perpendicular to the axis.

        :param rotation: The axis to rotate around (Rotation.X, Rotation.Y, or Rotation.Z)
        :param direction: The direction of the rotation (Direction.CW, Direction.CCW, Direction.DOUBLE)
        :return: None
        """

        order: dict[Layer, Layer] = {}
        faces: dict[Layer, Direction] = {}
        order, faces = CUBE_ROTATION_MAP.get((rotation, direction))

        # Swap around the faces
        old_layers: list[list[Color]] = [self.__cube.layers[layer] for layer in order.keys()]
        for index, new_layer in enumerate(order.values()):
            self.__cube.layers[new_layer] = old_layers[index]

        # Fix orientation
        for layer, layer_direction in faces.items():
            rotate_face(self.__cube, layer, layer_direction)

    def apply(self, algorithm: Algorithm) -> None:
        """
        Applies every move of an algorithm to the cube, in order.

        :param algorithm: The algorithm to perform
        :return: None
        """

        for move in algorithm.moves:
            self.turn(move)
