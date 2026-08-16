# Python imports
from typing import Callable

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.EdgeSlot import EdgeSlot
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.solve.cross import (
    ALIGNMENT_TABLE,
    EXTRACTION_TABLE,
    INSERTION_TABLE,
    ORIENTATION_TABLE,
    face_center_color,
    find_yellow_center_layer,
)
from rubik_cube_solver.solve.edge_search import search_edge
from rubik_cube_solver.solve.solve import Solve


class Solve3x3(Solve):
    """
    Human, CFOP-style solver for the 3x3 cube.

    Cases are recognized with `search_edge` and resolved through lookup tables of insertion
    algorithms and whole-cube `y` rotations, rather than a search algorithm. Currently implements
    only the cross step. The cross is built on the DOWN face with a yellow center, matching a
    default `Cube(3)`, which starts white-up / yellow-down.
    """

    def __init__(self, cube: Cube) -> None:
        """
        Constructor for the `Solve3x3` class.

        :param cube: The 3x3 cube to solve
        :return: None
        """

        if cube.size != 3:
            raise ValueError(f"Solve3x3 supports only 3x3 cubes, got size {cube.size}")

        super().__init__(cube)

    def _steps(self) -> list[Callable[[], None]]:
        """
        The ordered solving steps for a 3x3 cube.

        :return: The ordered solving steps
        """

        return [self._cross]

    def _cross(self) -> None:
        """
        Solves the yellow cross on the DOWN face.

        The cube may start in any orientation, so it is first rotated as a whole so the yellow
        center lands on DOWN. Each of the four side edges is then solved in turn, rotating the
        whole cube with `y` after each one so the next side comes to FRONT.

        :return: None
        """

        self._apply(Algorithm.from_str(ORIENTATION_TABLE[find_yellow_center_layer(self.cube)]))

        for _ in range(4):
            self._solve_cross_edge()
            self._apply(Algorithm.from_str("y"))

    def _solve_cross_edge(self) -> None:
        """
        Solves the cross edge matching the current FRONT center color.

        Does nothing if the edge is already correctly placed at DF. Otherwise extracts it into the
        UP layer (skipped if it is already there), aligns it to UF, then inserts it into DF with
        the correct orientation. The piece is re-searched after every applied algorithm, since a
        previous search result is no longer valid once the cube has moved.

        :return: None
        """

        front_color = face_center_color(self.cube, Layer.FRONT)
        slot, is_good = search_edge(self.cube, Color.YELLOW, front_color)

        if slot is EdgeSlot.DF and is_good:
            return

        if slot in EXTRACTION_TABLE:
            self._apply(Algorithm.from_str(EXTRACTION_TABLE[slot]))

        slot, _ = search_edge(self.cube, Color.YELLOW, front_color)
        self._apply(Algorithm.from_str(ALIGNMENT_TABLE[slot]))

        _, is_good = search_edge(self.cube, Color.YELLOW, front_color)
        self._apply(Algorithm.from_str(INSERTION_TABLE[is_good]))
