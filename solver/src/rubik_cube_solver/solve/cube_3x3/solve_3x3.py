# Python imports
from typing import Callable

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.EdgeSlot import EdgeSlot
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.solve.corner_search import search_corner
from rubik_cube_solver.solve.cube_3x3.cross import (
    CROSS_ALIGNMENT_TABLE,
    CROSS_EXTRACTION_TABLE,
    CROSS_INSERTION_TABLE,
    CROSS_ORIENTATION_TABLE,
    face_center_color,
    find_yellow_center_layer,
)
from rubik_cube_solver.solve.cube_3x3.f2l import (
    F2L_CORNER_ALIGNMENT_TABLE,
    F2L_CORNER_EXTRACTION_TABLE,
    F2L_EDGE_EXTRACTION_TABLE,
    F2L_PAIR_INSERTION_TABLE,
    front_color_on_up,
    is_pair_solved,
)
from rubik_cube_solver.solve.cube_3x3.oll import OLL_TABLE, up_corner_orientations, up_edge_orientations
from rubik_cube_solver.solve.cube_3x3.pll import PLL_TABLE, up_corner_permutation, up_edge_permutation
from rubik_cube_solver.solve.edge_search import search_edge
from rubik_cube_solver.solve.solve import Solve


class Solve3x3(Solve):
    """
    Human, CFOP-style solver for the 3x3 cube.

    Cases are recognized with `search_edge` and `search_corner` and resolved through lookup tables
    of insertion algorithms and whole-cube `y` rotations, rather than a search algorithm. It solves
    the cross, the first two layers, the orientation of the last layer and its permutation. The
    cross is built on the DOWN face with a yellow center, matching a default `Cube(3)`, which starts
    white-up / yellow-down. A cube that started in another orientation is solved in the orientation
    the cross rotated it into, so every face ends up showing one color but not necessarily the one
    it started with.
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

        return [self._cross, self._f2l, self._oll, self._pll]

    def _cross(self) -> None:
        """
        Solves the yellow cross on the DOWN face.

        The cube may start in any orientation, so it is first rotated as a whole so the yellow
        center lands on DOWN. Each of the four side edges is then solved in turn, rotating the
        whole cube with `y` after each one so the next side comes to FRONT.

        :return: None
        """

        self._apply(Algorithm.from_str(CROSS_ORIENTATION_TABLE[find_yellow_center_layer(self.cube)]))

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

        if slot in CROSS_EXTRACTION_TABLE:
            self._apply(Algorithm.from_str(CROSS_EXTRACTION_TABLE[slot]))

        slot, _ = search_edge(self.cube, Color.YELLOW, front_color)
        self._apply(Algorithm.from_str(CROSS_ALIGNMENT_TABLE[slot]))

        _, is_good = search_edge(self.cube, Color.YELLOW, front_color)
        self._apply(Algorithm.from_str(CROSS_INSERTION_TABLE[is_good]))

    def _f2l(self) -> None:
        """
        Solves the first two layers, on top of the cross the previous step leaves on DOWN.

        The four corner and edge pairs are solved in turn, rotating the whole cube with `y` after
        each one so the next pair comes to the front-right slot.

        :return: None
        """

        for _ in range(4):
            self._solve_f2l_pair()
            self._apply(Algorithm.from_str("y"))

    def _solve_f2l_pair(self) -> None:
        """
        Solves the pair matching the current FRONT and RIGHT center colors into the front-right slot.

        Does nothing if the pair already fills the slot. Otherwise both pieces are brought into the
        UP layer and inserted together. The corner goes first, because aligning it to UFR is what
        makes the edge extraction leave it in the UP layer, and it is aligned again afterwards since
        the extraction moves it along the UP layer. The pieces are re-searched after every applied
        algorithm, since a previous search result is no longer valid once the cube has moved.

        :return: None
        """

        front_color = face_center_color(self.cube, Layer.FRONT)
        right_color = face_center_color(self.cube, Layer.RIGHT)

        if is_pair_solved(self.cube, front_color, right_color):
            return

        corner_slot, _ = search_corner(self.cube, Color.YELLOW, front_color, right_color)
        if corner_slot in F2L_CORNER_EXTRACTION_TABLE:
            self._apply(Algorithm.from_str(F2L_CORNER_EXTRACTION_TABLE[corner_slot]))

        corner_slot, _ = search_corner(self.cube, Color.YELLOW, front_color, right_color)
        self._apply(Algorithm.from_str(F2L_CORNER_ALIGNMENT_TABLE[corner_slot]))

        edge_slot, _ = search_edge(self.cube, front_color, right_color)
        if edge_slot in F2L_EDGE_EXTRACTION_TABLE:
            self._apply(Algorithm.from_str(F2L_EDGE_EXTRACTION_TABLE[edge_slot]))

        corner_slot, _ = search_corner(self.cube, Color.YELLOW, front_color, right_color)
        self._apply(Algorithm.from_str(F2L_CORNER_ALIGNMENT_TABLE[corner_slot]))

        _, orientation = search_corner(self.cube, Color.YELLOW, front_color, right_color)
        edge_slot, _ = search_edge(self.cube, front_color, right_color)
        self._apply(
            Algorithm.from_str(
                F2L_PAIR_INSERTION_TABLE[(orientation, edge_slot, front_color_on_up(self.cube, edge_slot))]
            )
        )

    def _oll(self) -> None:
        """
        Orients the last layer, so the whole UP face ends up showing the UP center's color.

        The case is read straight off the cube as the orientation of each of the four UP corners
        and each of the four UP edges. A single table entry orients every piece of the layer at
        once, with the U turn that aligns the case already at its front, so this step is one
        lookup and one algorithm.

        :return: None
        """

        case = (up_corner_orientations(self.cube), up_edge_orientations(self.cube))
        self._apply(Algorithm.from_str(OLL_TABLE[case]))

    def _pll(self) -> None:
        """
        Permutes the last layer, finishing the cube.

        The case is read straight off the cube as the slot each of the four UP corners and each of
        the four UP edges belongs in. A single table entry places every piece of the layer at once,
        with both the U turn that aligns the case and the one that finishes the layer already part
        of it, so this step is one lookup and one algorithm.

        :return: None
        """

        case = (up_corner_permutation(self.cube), up_edge_permutation(self.cube))
        self._apply(Algorithm.from_str(PLL_TABLE[case]))
