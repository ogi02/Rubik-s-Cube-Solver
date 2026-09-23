# Python imports
from typing import Callable

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.solve.cube_3x3.solve_3x3 import Solve3x3
from rubik_cube_solver.solve.cube_nxn.centers import CENTERS_PLAN, build_nth_center
from rubik_cube_solver.solve.cube_nxn.edges import build_first_eight_edges
from rubik_cube_solver.solve.cube_nxn.last_centers import build_last_two_centers
from rubik_cube_solver.solve.cube_nxn.last_edges import build_last_four_edges
from rubik_cube_solver.solve.cube_nxn.parity import build_parity
from rubik_cube_solver.solve.cube_nxn.reduced_3x3 import as_3x3
from rubik_cube_solver.solve.solve import Solve


class SolveNxN(Solve):
    """
    Solver for big cubes, of size 4 and up.

    The cube is reduced to a 3x3 and then solved as one. The centers are built first: yellow, white,
    green and red, then blue and orange. Eight edges are then paired and stored on UP and DOWN, three of
    the last four are paired between the side faces, and the parity step pairs the twelfth and, on an
    even cube, fixes the edge flip and permutation parities. The reduced cube is finally solved like a
    3x3, with the CFOP method of `Solve3x3`.
    """

    def __init__(self, cube: Cube) -> None:
        """
        Constructor for the `SolveNxN` class.

        :param cube: The cube to solve, of size 4 or more
        :return: None
        """

        if cube.size < 4:
            raise ValueError(f"SolveNxN supports only cubes of size 4 or more, got size {cube.size}")

        super().__init__(cube)

    def _steps(self) -> dict[str, Callable[[], None]]:
        """
        The named solving steps for a big cube, in the order they are solved.

        The four centers are separate steps, since each goes up on a face of its own, while the edges
        and the parity that finishes them are one.

        :return: The solving steps by name, in order
        """

        return {
            "1st center": self._first_center,
            "2nd center": self._second_center,
            "3rd center": self._third_center,
            "4th center": self._fourth_center,
            "last 2 centers": self._last_two_centers,
            "edges": self._edges,
            "3x3 stage": self._solve_as_3x3,
        }

    def _first_center(self) -> None:
        """
        Builds the yellow center.

        :return: None
        """

        self._center(0)

    def _second_center(self) -> None:
        """
        Builds the white center, once yellow is built.

        :return: None
        """

        self._center(1)

    def _third_center(self) -> None:
        """
        Builds the green center, once yellow and white are built.

        :return: None
        """

        self._center(2)

    def _fourth_center(self) -> None:
        """
        Builds the red center, once yellow, white and green are built.

        :return: None
        """

        self._center(3)

    def _center(self, index: int) -> None:
        """
        Builds one of the first four centers, protecting the ones built before it.

        :param index: The position of the center in `CENTERS_PLAN`
        :return: None
        """

        done = [plan.color for plan in CENTERS_PLAN[:index]]
        moves, _ = build_nth_center(self.cube, CENTERS_PLAN[index], done)

        self._apply(Algorithm.from_str(" ".join(moves)))

    def _edges(self) -> None:
        """
        Pairs every edge, once all six centers are built.

        Eight edges are stored on UP and DOWN, three of the last four are paired between the side
        faces, and the parity step pairs the twelfth and fixes the parities an even cube can be left
        with.

        :return: None
        """

        self._first_eight_edges()
        self._last_four_edges()
        self._parity()

    def _last_two_centers(self) -> None:
        """
        Builds the blue and orange centers, once the first four are built.

        :return: None
        """

        self._apply(Algorithm.from_str(" ".join(build_last_two_centers(self.cube))))

    def _first_eight_edges(self) -> None:
        """
        Pairs eight edges and stores them on UP and DOWN, once every center is built.

        :return: None
        """

        self._apply(Algorithm.from_str(" ".join(build_first_eight_edges(self.cube))))

    def _last_four_edges(self) -> None:
        """
        Pairs three of the last four edges and gathers the wings of the fourth in one slot, once eight
        edges are stored on UP and DOWN.

        :return: None
        """

        self._apply(Algorithm.from_str(" ".join(build_last_four_edges(self.cube))))

    def _parity(self) -> None:
        """
        Pairs the twelfth edge and fixes the parities an even cube can be left with, once every other
        edge is paired.

        :return: None
        """

        self._apply(Algorithm.from_str(" ".join(build_parity(self.cube))))

    def _solve_as_3x3(self) -> None:
        """
        Solves the cube like a 3x3, once it is reduced.

        The 3x3 the cube stands for is solved with `Solve3x3`, and its solution is applied to the cube
        unchanged, since it holds only outer-face turns and whole-cube rotations, which turn a reduced
        big cube the same way.

        :return: None
        """

        self._apply(Solve3x3(as_3x3(self.cube)).solve())
