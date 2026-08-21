# Python imports
from typing import Callable

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.solve.cube_nxn.centers import (
    CENTERS_BUILD_TABLE,
    CENTERS_GREEN_FRONT_TABLE,
    CENTERS_WHITE_UP_TABLE,
    bar_column,
    bar_move,
    center_is_solved,
    finished_kind,
    fixed_center_layer,
    line_insertion,
    line_pieces,
    middle_completion,
    pole_eviction,
    preserved_line,
    solved_lines,
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

        return [self._centers]

    def _centers(self) -> None:
        """
        Solves the first four centers: white on UP, yellow on DOWN, green on FRONT and red on RIGHT.

        Each is built on the face the algorithms of the build are written for, and the cube is
        turned between them, so that one engine covers all four. The white and the yellow centers
        are built on DOWN, where the insertion restores the UP face and so the one built before it;
        the green and the red centers are built on RIGHT, where it restores the FRONT face instead.
        The turns add up to a full circle, so the cube ends the step upright, with the two centers
        left for the reduction on the LEFT and the BACK faces.

        :return: None
        """

        self._orient()

        for color, rotation, target in CENTERS_BUILD_TABLE:
            self._apply(Algorithm.from_str(rotation))
            self._build_center(color, target)

    def _orient(self) -> None:
        """
        Turns an odd cube so that its white fixed center is on UP and its green one is on FRONT.

        The fixed centers of an odd cube never leave their face, so they decide the color of every
        face and the cube has to be turned to match before anything is built. An even cube has no
        fixed center, so the first center is built on whichever face is already there and the
        colors of the rest follow from it.

        :return: None
        """

        if self.cube.size % 2 == 0:
            return

        white = CENTERS_WHITE_UP_TABLE[fixed_center_layer(self.cube, Color.WHITE)]
        self._apply(Algorithm.from_str(white))

        green = CENTERS_GREEN_FRONT_TABLE[fixed_center_layer(self.cube, Color.GREEN)]
        self._apply(Algorithm.from_str(green))

    def _build_center(self, color: Color, target: Layer) -> None:
        """
        Builds the center of the given color, one line of the face at a time.

        A line is assembled as a bar on the staging face before it is inserted, because an
        insertion replaces the line it fills as a whole. The middle line of an odd cube is its own
        opposite and no insertion can fill it, so it is filled first, by an algorithm of its own,
        while the face is still empty and every piece of the cube is free to be fetched.

        :param color: The color of the center to build
        :param target: The face to build it on
        :return: None
        """

        self._repeat(lambda: pole_eviction(self.cube, color))

        if self.cube.size % 2:
            self._build_middle_line(color, target)

        while not center_is_solved(self.cube, color, target):
            preserved = preserved_line(self.cube.size, solved_lines(self.cube, color, target))
            self._build_line(color, target, bar_column(self.cube.size, target, preserved))
            self._apply(Algorithm.from_str(line_insertion(self.cube.size, target, preserved)))

    def _build_middle_line(self, color: Color, target: Layer) -> None:
        """
        Fills the middle line of an odd cube, the one no insertion can fill.

        The completion lays the bar across the middle line, and the face is then turned a quarter
        so that the finished line runs the way every later insertion expects. Every other line is
        still empty at that point, so nothing the quarter turn moves is anything but scrap.

        :param color: The color of the center being built
        :param target: The face being built
        :return: None
        """

        middle = self.cube.size // 2
        kind = finished_kind(self.cube.size, target, middle)

        if line_pieces(self.cube, target, color, (kind, middle)) < self.cube.size - 2:
            self._build_line(color, target, middle)
            self._apply(Algorithm.from_str(middle_completion(self.cube.size, target)))

        self._apply(Algorithm.from_str(target.value))

    def _build_line(self, color: Color, target: Layer, column: int) -> None:
        """
        Assembles a bar of center pieces in one column of the staging face.

        :param color: The color of the center being built
        :param target: The face being built
        :param column: The column of the staging face the bar is assembled in
        :return: None
        """

        self._repeat(lambda: bar_move(self.cube, color, target, column))

    def _repeat(self, next_algorithm: Callable[[], str]) -> None:
        """
        Applies the algorithms a step hands out, one at a time, until it hands out none.

        The cube is read again after every one of them, since the locations a search returned are
        stale as soon as the cube has moved.

        :param next_algorithm: The callable returning the next algorithm, or an empty string
        :return: None
        """

        algorithm = next_algorithm()

        while algorithm:
            self._apply(Algorithm.from_str(algorithm))
            algorithm = next_algorithm()
