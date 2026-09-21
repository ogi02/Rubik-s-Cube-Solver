# Python imports
from typing import Callable

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.solve.cube_nxn.centers import build_first_four_centers
from rubik_cube_solver.solve.solve import Solve


class SolveNxN(Solve):
    """
    Solver for even big cubes, of size 4, 6, 8 and up.

    Its only step so far is the first four centers - yellow, white, green and red - so a cube comes
    back with those four centers built and the rest of it untouched, not solved.
    """

    def __init__(self, cube: Cube) -> None:
        """
        Constructor for the `SolveNxN` class.

        :param cube: The cube to solve, of even size 4 or more
        :return: None
        """

        if cube.size < 4 or cube.size % 2:
            raise ValueError(f"SolveNxN supports only even cubes of size 4 or more, got size {cube.size}")

        super().__init__(cube)

    def _steps(self) -> list[Callable[[], None]]:
        """
        The ordered solving steps for an even big cube.

        :return: The ordered solving steps
        """

        return [self._first_four_centers]

    def _first_four_centers(self) -> None:
        """
        Builds the yellow, white, green and red centers.

        :return: None
        """

        self._apply(Algorithm.from_str(" ".join(build_first_four_centers(self.cube))))
