# Python imports
from abc import ABC, abstractmethod
from typing import Callable

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.cube_rotation.rotator import Rotator
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

    def solve(self) -> Algorithm:
        """
        Solves the cube by validating its state and running every step in order.

        Once all steps have run, the accumulated solution has its rotations removed and is then
        reduced by cancelling adjacent moves, in that order, since rotations are cancellation
        barriers and must be gone before moves either side of one can collapse into each other.

        :return: The solution
        """

        Validator().validate(self.__cube)

        for step in self._steps():
            step()

        self.__solution.remove_rotations()
        self.__solution.cancel_moves()

        return self.__solution

    @abstractmethod
    def _steps(self) -> list[Callable[[], None]]:
        """
        The ordered solving steps for this cube type.

        :return: The ordered solving steps
        """

    def _apply(self, algorithm: Algorithm) -> None:
        """
        Runs an algorithm on the cube and records it in the solution.

        :param algorithm: The algorithm to apply
        :return: None
        """

        self.__rotator.apply(algorithm)
        self.__solution.merge(algorithm)
