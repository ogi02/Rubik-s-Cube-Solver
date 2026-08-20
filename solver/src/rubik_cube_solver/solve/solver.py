# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.solve.cube_2x2.solve_2x2 import Solve2x2
from rubik_cube_solver.solve.cube_3x3.solve_3x3 import Solve3x3
from rubik_cube_solver.solve.solve import Solve


def create_solver(cube: Cube) -> Solve:
    """
    Creates the solver for a cube, chosen by its size.

    This is the single entry point for solving: a caller passes any cube and gets back the concrete
    `Solve` subclass that handles that size, without naming it or checking the size itself. The
    returned solver is an ordinary `Solve`, so the cube being solved and the solution collected so
    far stay reachable through it, and `solve()` is called on it as usual.

    :param cube: The cube to solve
    :return: The solver for the cube's size
    """

    match cube.size:
        case 2:
            return Solve2x2(cube)
        case 3:
            return Solve3x3(cube)
        case _:
            raise ValueError(f"No solver for cubes of size {cube.size}, only 2x2 and 3x3 are supported")
