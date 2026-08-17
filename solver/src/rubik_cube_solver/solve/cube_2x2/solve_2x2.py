# Python imports
from typing import Callable

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.CornerSlot import CornerSlot
from rubik_cube_solver.solve.corner_search import search_corner
from rubik_cube_solver.solve.cube_2x2.first_layer import (
    FIRST_LAYER_ALIGNMENT_TABLE,
    FIRST_LAYER_CORNER_COLORS,
    FIRST_LAYER_EXTRACTION_TABLE,
    FIRST_LAYER_INSERTION_TABLE,
)
from rubik_cube_solver.solve.solve import Solve


class Solve2x2(Solve):
    """
    Human, layer-by-layer solver for the 2x2 cube.

    Cases are recognized with `search_corner` and resolved through lookup tables of algorithms and
    whole-cube `y` rotations, rather than a search algorithm. It solves the first layer, the yellow
    one, on the DOWN face. A 2x2 has no centers, so no face carries a fixed color: the layer is
    built in the color scheme of a solved cube instead, which is why the cube ends up in the
    orientation of a default `Cube(2)` whatever orientation it started in.
    """

    def __init__(self, cube: Cube) -> None:
        """
        Constructor for the `Solve2x2` class.

        :param cube: The 2x2 cube to solve
        :return: None
        """

        if cube.size != 2:
            raise ValueError(f"Solve2x2 supports only 2x2 cubes, got size {cube.size}")

        super().__init__(cube)

    def _steps(self) -> list[Callable[[], None]]:
        """
        The ordered solving steps for a 2x2 cube.

        :return: The ordered solving steps
        """

        return [self._first_layer]

    def _first_layer(self) -> None:
        """
        Solves the yellow layer on the DOWN face.

        The four corners are solved in turn, rotating the whole cube with `y` after each one so the
        next corner's slot comes to the front-right. The four rotations add up to a full turn, so
        the cube ends the step in the orientation it started it in.

        :return: None
        """

        for front_color, right_color in FIRST_LAYER_CORNER_COLORS:
            self._solve_first_layer_corner(front_color, right_color)
            self._apply(Algorithm.from_str("y"))

    def _solve_first_layer_corner(self, front_color: Color, right_color: Color) -> None:
        """
        Solves the corner with the given two side colors into the front-right slot of the DOWN layer.

        Does nothing if the corner already sits there with its yellow sticker on DOWN. Otherwise it
        is extracted into the UP layer (skipped if it is already there), aligned to UFR, then
        inserted into DFR by an algorithm keyed by the orientation it is aligned in. The corner is
        re-searched after every applied algorithm, since a previous search result is no longer valid
        once the cube has moved.

        :param front_color: The color the corner shows on FRONT once solved
        :param right_color: The color the corner shows on RIGHT once solved
        :return: None
        """

        slot, orientation = search_corner(self.cube, Color.YELLOW, front_color, right_color)

        if slot is CornerSlot.DFR and orientation == 0:
            return

        if slot in FIRST_LAYER_EXTRACTION_TABLE:
            self._apply(Algorithm.from_str(FIRST_LAYER_EXTRACTION_TABLE[slot]))

        slot, _ = search_corner(self.cube, Color.YELLOW, front_color, right_color)
        self._apply(Algorithm.from_str(FIRST_LAYER_ALIGNMENT_TABLE[slot]))

        _, orientation = search_corner(self.cube, Color.YELLOW, front_color, right_color)
        self._apply(Algorithm.from_str(FIRST_LAYER_INSERTION_TABLE[orientation]))
