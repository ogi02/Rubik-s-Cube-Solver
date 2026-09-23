# Python imports
from abc import ABC, abstractmethod
from typing import Callable

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.cube_rotation.rotator import Rotator
from rubik_cube_solver.enums.Rotation import Rotation
from rubik_cube_solver.validator.validator import Validator


class Solve(ABC):
    """
    Base class for solving a cube of any size.

    It holds the cube being solved, a `Rotator` to perform moves on it and the algorithm
    accumulated so far. Subclasses supply the ordered steps that make up their solving method
    for their cube type.
    """

    def __init__(self, cube: Cube) -> None:
        """
        Constructor for the `Solve` class.

        :param cube: The cube to solve
        :return: None
        """

        self.__cube = cube
        self.__rotator = Rotator(cube)
        self.__solution = Algorithm([])
        self.__step = Algorithm([])

    @property
    def cube(self) -> Cube:
        """
        Cube getter

        :return: The cube
        """

        return self.__cube

    @cube.setter
    def cube(self, cube: Cube) -> None:
        """
        Cube setter

        :param cube: The cube
        :return: None
        """

        self.__cube = cube
        self.__rotator.cube = cube

    @property
    def solution(self) -> Algorithm:
        """
        Solution getter

        :return: The solution
        """

        return self.__solution

    @solution.setter
    def solution(self, solution: Algorithm) -> None:
        """
        Solution setter

        :param solution: The solution
        :return: None
        """

        self.__solution = solution

    def solve(self, steps: bool = False) -> Algorithm | dict[str, Algorithm]:
        """
        Solves the cube by validating its state and running every step in order.

        Once all steps have run, the accumulated solution has its rotations removed and is then
        reduced by cancelling adjacent moves, in that order, since rotations are cancellation
        barriers and must be gone before moves either side of one can collapse into each other.

        Asked for the steps, the same solution comes back split into the named steps of the method,
        in the order they were solved. Every step holds layer turns only, written in the orientation
        the cube started in, so the steps can be read, printed or sent on one at a time and still
        describe the same solve.

        :param steps: Whether to return the solution split into the steps of the method
        :return: The solution, or the solution of each step by name
        """

        Validator().validate(self.__cube)

        solved: dict[str, Algorithm] = {}

        for name, step in self._steps().items():
            self.__step = Algorithm([])
            step()
            solved[name] = self.__step

        # Removing the rotations keeps every layer turn, in order, so each step can be cut back out
        # of the result by the number of turns it contributed
        turns = {
            name: sum(1 for move in algorithm.moves if not isinstance(move.layer, Rotation))
            for name, algorithm in solved.items()
        }
        self.__solution = Algorithm([move for algorithm in solved.values() for move in algorithm.moves])
        self.__solution.remove_rotations()

        if steps:
            solved = self.__split(turns)

        self.__solution.cancel_moves()

        return solved if steps else self.__solution

    def __split(self, turns: dict[str, int]) -> dict[str, Algorithm]:
        """
        Cuts the solution back into its steps, by how many turns each one contributed.

        :param turns: The number of layer turns each step contributed
        :return: The solution of each step by name
        """

        solved: dict[str, Algorithm] = {}
        start = 0

        for name, count in turns.items():
            step = Algorithm(self.__solution.moves[start : start + count])
            step.cancel_moves()
            solved[name] = step
            start += count

        return solved

    @abstractmethod
    def _steps(self) -> dict[str, Callable[[], None]]:
        """
        The named solving steps for this cube type, in the order they are solved.

        :return: The solving steps by name, in order
        """

    def _apply(self, algorithm: Algorithm) -> None:
        """
        Runs an algorithm on the cube and records it in the solution.

        :param algorithm: The algorithm to apply
        :return: None
        """

        self.__rotator.apply(algorithm)
        self.__solution.merge(algorithm)
        self.__step.merge(algorithm)
