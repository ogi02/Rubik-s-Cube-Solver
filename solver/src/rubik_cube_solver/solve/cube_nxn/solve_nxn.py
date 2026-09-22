# Python imports
from typing import Callable

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.solve.cube_nxn.centers import build_first_four_centers
from rubik_cube_solver.solve.cube_nxn.edges import build_first_eight_edges
from rubik_cube_solver.solve.cube_nxn.last_centers import build_last_two_centers
from rubik_cube_solver.solve.cube_nxn.last_edges import build_last_four_edges
from rubik_cube_solver.solve.solve import Solve


class SolveNxN(Solve):
    """
    Solver for big cubes, of size 4 and up.

    Its steps so far build the centers: first yellow, white, green and red, then blue and orange. Eight
    edges are then paired and stored on UP and DOWN, and three of the last four are paired between the
    side faces, so a cube comes back with every center built, eleven of its edges paired, the wings of
    the twelfth in one slot but not necessarily paired, and its corners not solved.
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

    def _steps(self) -> list[Callable[[], None]]:
        """
        The ordered solving steps for a big cube.

        :return: The ordered solving steps
        """

        return [self._first_four_centers, self._last_two_centers, self._first_eight_edges, self._last_four_edges]

    def _first_four_centers(self) -> None:
        """
        Builds the yellow, white, green and red centers.

        :return: None
        """

        self._apply(Algorithm.from_str(" ".join(build_first_four_centers(self.cube))))

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
