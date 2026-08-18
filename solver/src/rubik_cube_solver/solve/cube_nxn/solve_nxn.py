# Python imports
from typing import Callable

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.solve.cube_nxn.first_centers import (
    FIRST_CENTERS_ORIENTATION_TABLE,
    down_extraction,
    fill_schedule,
    fixed_center_layer,
    line_insertion,
    staging_move,
    up_eviction,
)
from rubik_cube_solver.solve.solve import Solve


class SolveNxN(Solve):
    """
    Human, reduction solver for big cubes, of size 4 and up.

    The centers are built face by face and the pieces are recognized with `search_center`, rather
    than by a search algorithm. A center piece is interchangeable with the three others of its color
    and position type, so a face is solved once every cell of it carries the right color, whichever
    piece ended up where.
    """

    def __init__(self, cube: Cube) -> None:
        """
        Constructor for the `SolveNxN` class.

        :param cube: The big cube to solve
        :return: None
        """

        if cube.size < 4:
            raise ValueError(f"SolveNxN supports only big cubes, got size {cube.size}")

        super().__init__(cube)

    def _steps(self) -> list[Callable[[], None]]:
        """
        The ordered solving steps for a big cube.

        :return: The ordered solving steps
        """

        return [self._first_centers]

    def _first_centers(self) -> None:
        """
        Solves the first two centers, the yellow one on DOWN and the white one on UP.

        Both are built on the UP face, since the algorithm that inserts a line into it is the one
        that leaves the DOWN face untouched. The yellow center is built first and turned to DOWN
        with `x2`, which brings the white face up in its place, and the white center is then built
        without ever disturbing the yellow one.

        An odd cube has fixed centers, so the color of every face is already decided and the cube is
        turned to match before anything is built. An even cube has none, and the yellow center is
        built on whichever face is UP.

        :return: None
        """

        if self.cube.size % 2:
            layer = fixed_center_layer(self.cube, Color.YELLOW)
            self._apply(Algorithm.from_str(FIRST_CENTERS_ORIENTATION_TABLE[layer]))

        self._build_center(Color.YELLOW)
        self._apply(Algorithm.from_str("x2"))
        self._build_center(Color.WHITE)

    def _build_center(self, color: Color) -> None:
        """
        Builds the center of the given color on the UP face.

        The DOWN and UP faces are emptied of that color first, since a piece on DOWN cannot be
        fetched once the UP face holds solved pieces and a piece already on UP is one the staging
        cannot reach. The face is then filled one line at a time.

        :param color: The color of the center to build
        :return: None
        """

        self._clear_down_face(color)
        self._clear_up_face(color)

        for col, turn, rotation in fill_schedule(self.cube.size):
            self._fill_line(color, col, turn)
            self._apply(Algorithm.from_str(rotation))

    def _clear_down_face(self, color: Color) -> None:
        """
        Takes every center piece of the given color off the DOWN face.

        :param color: The color of the center being built
        :return: None
        """

        algorithm = down_extraction(self.cube, color)

        while algorithm:
            self._apply(Algorithm.from_str(algorithm))
            algorithm = down_extraction(self.cube, color)

    def _clear_up_face(self, color: Color) -> None:
        """
        Takes every center piece of the given color off the UP face.

        :param color: The color of the center being built
        :return: None
        """

        algorithm = up_eviction(self.cube, color)

        while algorithm:
            self._apply(Algorithm.from_str(algorithm))
            algorithm = up_eviction(self.cube, color)

    def _fill_line(self, color: Color, col: int, turn: str) -> None:
        """
        Stages a whole column of center pieces on the FRONT face and inserts it into the UP face.

        The column is staged before it is inserted, because the insertion replaces the line it fills
        as a whole. The cube is searched again after every staged piece, since the previous search
        result is no longer valid once the cube has moved.

        :param color: The color of the center being built
        :param col: The column of the FRONT face the pieces are staged in
        :param turn: The direction of the U turn of the insertion, one of "", "'" and "2"
        :return: None
        """

        algorithm = staging_move(self.cube, color, col)

        while algorithm:
            self._apply(Algorithm.from_str(algorithm))
            algorithm = staging_move(self.cube, color, col)

        self._apply(Algorithm.from_str(line_insertion(self.cube.size, col, turn)))
