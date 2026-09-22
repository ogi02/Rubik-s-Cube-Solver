# Python imports
from typing import Callable

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.solve.cube_3x3.solve_3x3 import Solve3x3
from rubik_cube_solver.solve.cube_nxn.centers import build_first_four_centers
from rubik_cube_solver.solve.cube_nxn.edges import build_first_eight_edges
from rubik_cube_solver.solve.cube_nxn.last_centers import build_last_two_centers
from rubik_cube_solver.solve.cube_nxn.last_edges import build_last_four_edges
from rubik_cube_solver.solve.cube_nxn.parity import build_parity
from rubik_cube_solver.solve.cube_nxn.reduced_3x3 import as_3x3
from rubik_cube_solver.solve.cube_nxn.view import held_in_view
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

    def _steps(self) -> list[Callable[[], None]]:
        """
        The ordered solving steps for a big cube.

        :return: The ordered solving steps
        """

        return [
            self._first_four_centers,
            self._last_two_centers,
            self._first_eight_edges,
            self._last_four_edges,
            self._parity,
            self._solve_as_3x3,
        ]

    def _first_four_centers(self) -> None:
        """
        Builds the yellow, white, green and red centers.

        With the grips kept, each center is built with the cube held so the face it is being built on
        faces a viewer, since white is built on LEFT and green and red on DOWN, all of which point
        away from one. The pieces turned are the same either way.

        :return: None
        """

        self._apply(Algorithm.from_str(" ".join(build_first_four_centers(self.cube, in_view=self._keep_grips))))

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

        self._apply(Algorithm.from_str(" ".join(self._in_view(build_first_eight_edges(self.cube)))))

    def _last_four_edges(self) -> None:
        """
        Pairs three of the last four edges and gathers the wings of the fourth in one slot, once eight
        edges are stored on UP and DOWN.

        :return: None
        """

        self._apply(Algorithm.from_str(" ".join(self._in_view(build_last_four_edges(self.cube)))))

    def _in_view(self, moves: list[str]) -> list[str]:
        """
        Holds an edge step's algorithms in one grip, so the edge being paired can be seen throughout.

        Both edge steps pair into FL, whose left half points away from a viewer, so the cube is turned
        to bring that half forward and turned back afterwards. The regrips the method makes between
        edges are settled out first, leaving the cube held still for the whole step and turned once at
        the finish, since a slot that keeps moving is harder to follow than one that stays put. The
        same wings are paired either way.

        :param moves: The algorithms of the step
        :return: The algorithms, held in one grip to be seen if the grips are kept
        """

        if not self._keep_grips:
            return moves

        algorithm = Algorithm.from_str(" ".join(moves))
        algorithm.settle_rotations()

        return held_in_view([str(algorithm)], Layer.LEFT)

    def _parity(self) -> None:
        """
        Pairs the twelfth edge and fixes the parities an even cube can be left with, once every other
        edge is paired.

        It finishes the edges, so with the grips kept it holds the cube still the same way the edge
        steps do, turning once at the end rather than partway through.

        :return: None
        """

        algorithm = Algorithm.from_str(" ".join(build_parity(self.cube)))

        if self._keep_grips:
            algorithm.settle_rotations()

        self._apply(algorithm)

    def _solve_as_3x3(self) -> None:
        """
        Solves the cube like a 3x3, once it is reduced.

        The 3x3 the cube stands for is solved with `Solve3x3`, and its solution is applied to the cube
        unchanged, since it holds only outer-face turns and whole-cube rotations, which turn a reduced
        big cube the same way. The grips are kept or dropped exactly as they are for the whole solve, so
        the reduced phase turns the cube between its cross, F2L, OLL and PLL pieces like any other step.

        :return: None
        """

        self._apply(Solve3x3(as_3x3(self.cube)).solve(keep_grips=self._keep_grips))
