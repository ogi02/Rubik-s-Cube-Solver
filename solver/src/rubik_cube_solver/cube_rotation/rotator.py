# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.face_stickers_rotation import rotate_face
from rubik_cube_solver.cube_rotation.move import Move
from rubik_cube_solver.cube_rotation.side_stickers_rotation import rotate_sides
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

        Possible faces: 'U', 'D', 'L', 'R', 'F', 'B'.
        Possible directions: clockwise, counter-clockwise, double

        :param move: The move to perform
        :return: None
        """

        # Rotate the face stickers
        rotate_face(self.__cube, move.layer, move.direction)

        # Rotate the side stickers
        rotate_sides(self.__cube, move.layer, move.direction, move.layer_amount)

    def rotate(self, rotation: Rotation, amount: int) -> None:
        """
        Applies a whole-cube rotation around the specified axis.

        The rotation remaps all 6 faces of the cube according to the axis
        and also rotates the stickers of the two faces perpendicular to the axis.

        :param rotation: The axis to rotate around (Rotation.X, Rotation.Y, or Rotation.Z)
        :param amount: Number of quarter-turns: 1 (CW), 2 (double), or -1 (CCW)
        :return: None
        :raises ValueError: If amount is not in {-1, 1, 2}
        """

        if amount not in (-1, 1, 2):
            raise ValueError(f"Invalid rotation amount: {amount}")

        # Dispatch to the appropriate axis handler
        if rotation == Rotation.X:
            self.__rotate_x(amount)
        elif rotation == Rotation.Y:
            self.__rotate_y(amount)
        elif rotation == Rotation.Z:
            self.__rotate_z(amount)

    def __rotate_x(self, amount: int) -> None:
        """
        Rotates the cube around the x-axis.

        :param amount: 1 (CW, same as R), -1 (CCW), or 2 (double)
        :return: None
        """
        layers = self.__cube.layers

        # Save copies of all cycling faces
        old_up = list(layers[Layer.UP])
        old_front = list(layers[Layer.FRONT])
        old_down = list(layers[Layer.DOWN])
        old_back = list(layers[Layer.BACK])

        if amount == 1:
            layers[Layer.UP] = old_front
            layers[Layer.FRONT] = old_down
            layers[Layer.DOWN] = old_back
            layers[Layer.BACK] = old_up
            # Fix BACK and DOWN sticker orientation (180 degree rotation needed
            # for faces moving into/from BACK position due to 2D representation)
            rotate_face(self.__cube, Layer.DOWN, Direction.DOUBLE)
            rotate_face(self.__cube, Layer.BACK, Direction.DOUBLE)
            # Perpendicular faces
            rotate_face(self.__cube, Layer.RIGHT, Direction.CW)
            rotate_face(self.__cube, Layer.LEFT, Direction.CCW)

        elif amount == -1:
            layers[Layer.UP] = old_back
            layers[Layer.FRONT] = old_up
            layers[Layer.DOWN] = old_front
            layers[Layer.BACK] = old_down
            # Fix sticker orientation for BACK-related transfers
            rotate_face(self.__cube, Layer.UP, Direction.DOUBLE)
            rotate_face(self.__cube, Layer.BACK, Direction.DOUBLE)
            # Perpendicular faces
            rotate_face(self.__cube, Layer.RIGHT, Direction.CCW)
            rotate_face(self.__cube, Layer.LEFT, Direction.CW)

        elif amount == 2:
            layers[Layer.UP] = old_down
            layers[Layer.DOWN] = old_up
            layers[Layer.FRONT] = old_back
            layers[Layer.BACK] = old_front
            # Fix sticker orientation
            rotate_face(self.__cube, Layer.FRONT, Direction.DOUBLE)
            rotate_face(self.__cube, Layer.BACK, Direction.DOUBLE)
            # Perpendicular faces
            rotate_face(self.__cube, Layer.RIGHT, Direction.DOUBLE)
            rotate_face(self.__cube, Layer.LEFT, Direction.DOUBLE)

    def __rotate_y(self, amount: int) -> None:
        """
        Rotates the cube around the y-axis.

        :param amount: 1 (CW, same as U), -1 (CCW), or 2 (double)
        :return: None
        """
        layers = self.__cube.layers

        old_front = list(layers[Layer.FRONT])
        old_right = list(layers[Layer.RIGHT])
        old_back = list(layers[Layer.BACK])
        old_left = list(layers[Layer.LEFT])

        if amount == 1:
            layers[Layer.FRONT] = old_right
            layers[Layer.RIGHT] = old_back
            layers[Layer.BACK] = old_left
            layers[Layer.LEFT] = old_front
            # No sticker rotation on cycling faces (all in horizontal band)
            # Perpendicular faces
            rotate_face(self.__cube, Layer.UP, Direction.CW)
            rotate_face(self.__cube, Layer.DOWN, Direction.CCW)

        elif amount == -1:
            layers[Layer.FRONT] = old_left
            layers[Layer.LEFT] = old_back
            layers[Layer.BACK] = old_right
            layers[Layer.RIGHT] = old_front
            # Perpendicular faces
            rotate_face(self.__cube, Layer.UP, Direction.CCW)
            rotate_face(self.__cube, Layer.DOWN, Direction.CW)

        elif amount == 2:
            layers[Layer.FRONT] = old_back
            layers[Layer.BACK] = old_front
            layers[Layer.LEFT] = old_right
            layers[Layer.RIGHT] = old_left
            # Perpendicular faces
            rotate_face(self.__cube, Layer.UP, Direction.DOUBLE)
            rotate_face(self.__cube, Layer.DOWN, Direction.DOUBLE)

    def __rotate_z(self, amount: int) -> None:
        """
        Rotates the cube around the z-axis.

        :param amount: 1 (CW, same as F), -1 (CCW), or 2 (double)
        :return: None
        """
        layers = self.__cube.layers

        old_up = list(layers[Layer.UP])
        old_right = list(layers[Layer.RIGHT])
        old_down = list(layers[Layer.DOWN])
        old_left = list(layers[Layer.LEFT])

        if amount == 1:
            layers[Layer.UP] = old_left
            layers[Layer.RIGHT] = old_up
            layers[Layer.DOWN] = old_right
            layers[Layer.LEFT] = old_down
            # All cycling faces need CW sticker rotation
            rotate_face(self.__cube, Layer.UP, Direction.CW)
            rotate_face(self.__cube, Layer.RIGHT, Direction.CW)
            rotate_face(self.__cube, Layer.DOWN, Direction.CW)
            rotate_face(self.__cube, Layer.LEFT, Direction.CW)
            # Perpendicular faces
            rotate_face(self.__cube, Layer.FRONT, Direction.CW)
            rotate_face(self.__cube, Layer.BACK, Direction.CCW)

        elif amount == -1:
            layers[Layer.UP] = old_right
            layers[Layer.RIGHT] = old_down
            layers[Layer.DOWN] = old_left
            layers[Layer.LEFT] = old_up
            # All cycling faces need CCW sticker rotation
            rotate_face(self.__cube, Layer.UP, Direction.CCW)
            rotate_face(self.__cube, Layer.RIGHT, Direction.CCW)
            rotate_face(self.__cube, Layer.DOWN, Direction.CCW)
            rotate_face(self.__cube, Layer.LEFT, Direction.CCW)
            # Perpendicular faces
            rotate_face(self.__cube, Layer.FRONT, Direction.CCW)
            rotate_face(self.__cube, Layer.BACK, Direction.CW)

        elif amount == 2:
            layers[Layer.UP] = old_down
            layers[Layer.DOWN] = old_up
            layers[Layer.LEFT] = old_right
            layers[Layer.RIGHT] = old_left
            # All cycling faces need 180 sticker rotation
            rotate_face(self.__cube, Layer.UP, Direction.DOUBLE)
            rotate_face(self.__cube, Layer.RIGHT, Direction.DOUBLE)
            rotate_face(self.__cube, Layer.DOWN, Direction.DOUBLE)
            rotate_face(self.__cube, Layer.LEFT, Direction.DOUBLE)
            # Perpendicular faces
            rotate_face(self.__cube, Layer.FRONT, Direction.DOUBLE)
            rotate_face(self.__cube, Layer.BACK, Direction.DOUBLE)
