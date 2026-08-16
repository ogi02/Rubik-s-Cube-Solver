# Python imports
from typing import Callable

import pytest

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.solve.solve import Solve


class _StubSolve(Solve):
    """
    Minimal `Solve` subclass for testing.

    Each step applies one of the given algorithm strings, in order, and records the algorithm
    string in `calls` before applying it, so tests can assert both the order the steps ran in
    and the effect each step had on the cube and solution.
    """

    def __init__(self, cube: Cube, algorithms: list[str]) -> None:
        """
        Constructor for the `_StubSolve` class.

        :param cube: The cube to solve
        :param algorithms: The algorithm string applied by each step, in order
        :return: None
        """

        super().__init__(cube)
        self.__algorithms = algorithms
        self.calls: list[str] = []

    def _steps(self) -> list[Callable[[], None]]:
        """
        Builds one step per algorithm string given to the constructor.

        :return: The ordered solving steps
        """

        return [self.__make_step(algorithm) for algorithm in self.__algorithms]

    def __make_step(self, algorithm: str) -> Callable[[], None]:
        """
        Builds a single step that records and applies the given algorithm string.

        :param algorithm: The algorithm string the step applies
        :return: The step
        """

        def step() -> None:
            self.calls.append(algorithm)
            self._apply(Algorithm.from_str(algorithm))

        return step


class _IncompleteSolve(Solve):
    """
    `Solve` subclass that does not implement `_steps`, used to prove that abstractness is
    enforced on every subclass, not just on `Solve` itself.
    """


class TestSolveInit:
    def test_stores_cube_and_starts_with_empty_solution(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that the constructor stores the given cube and starts with an empty solution.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(3, "")
        solve = _StubSolve(cube, [])

        # Assert
        assert solve.cube is cube
        assert solve.solution == Algorithm([])

    def test_solve_cannot_be_instantiated_directly(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that `Solve` cannot be instantiated directly since it is abstract.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(3, "")

        # Assert
        with pytest.raises(TypeError):
            Solve(cube)

    def test_subclass_without_steps_cannot_be_instantiated(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that a subclass which does not implement `_steps` is still abstract and cannot be
        instantiated.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(3, "")

        # Assert
        with pytest.raises(TypeError):
            _IncompleteSolve(cube)


class TestSolveCube:
    def test_getter(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that the cube getter returns the stored cube.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(3, "")
        solve = _StubSolve(cube, [])

        # Assert
        assert solve.cube is cube

    def test_setter_repoints_the_rotator(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that the cube setter swaps the stored cube and re-points the internal rotator to
        it, proven by applying an algorithm after the swap and checking that only the new cube
        changed.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cubes
        original_cube = generate_cube(3, "")
        new_cube = generate_cube(3, "")
        original_state = str(original_cube)
        new_state = str(new_cube)

        solve = _StubSolve(original_cube, [])
        solve.cube = new_cube
        solve._apply(Algorithm.from_str("R"))

        # Assert
        assert str(original_cube) == original_state
        assert str(new_cube) != new_state


class TestSolveSolution:
    def test_getter(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that the solution getter returns the stored solution.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(3, "")
        solve = _StubSolve(cube, [])

        # Assert
        assert solve.solution == Algorithm([])

    def test_setter(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that the solution setter replaces the stored solution.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(3, "")
        solve = _StubSolve(cube, [])
        solve.solution = Algorithm.from_str("R U")

        # Assert
        assert solve.solution == Algorithm.from_str("R U")


class TestSolveApply:
    def test_turns_cube_and_records_moves(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that applying an algorithm turns the cube and records its moves in the solution.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cubes
        cube = generate_cube(3, "")
        expected_cube = generate_cube(3, "R")
        solve = _StubSolve(cube, [])
        solve._apply(Algorithm.from_str("R"))

        # Assert
        assert str(cube) == str(expected_cube)
        assert solve.solution == Algorithm.from_str("R")

    def test_accumulates_across_calls(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that two `_apply` calls accumulate their moves into the solution.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(3, "")
        solve = _StubSolve(cube, [])
        solve._apply(Algorithm.from_str("R"))
        solve._apply(Algorithm.from_str("U"))

        # Assert
        assert solve.solution == Algorithm.from_str("R U")

    def test_cancelling_moves_leave_an_empty_solution_and_solved_cube(
        self, generate_cube: Callable[[int, str], Cube]
    ) -> None:
        """
        Tests that applying `R` followed by `R'` cancels out, leaving an empty solution and a
        solved cube, since `merge` cancels moves across the accumulated solution.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cubes
        cube = generate_cube(3, "")
        solved_cube = generate_cube(3, "")
        solve = _StubSolve(cube, [])
        solve._apply(Algorithm.from_str("R"))
        solve._apply(Algorithm.from_str("R'"))

        # Assert
        assert str(cube) == str(solved_cube)
        assert solve.solution == Algorithm([])


class TestSolveSolve:
    def test_runs_every_step_in_order_and_returns_the_solution(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that `solve` runs every step returned by `_steps`, in order, and returns the
        accumulated solution.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(3, "")
        solve = _StubSolve(cube, ["R", "U"])
        result = solve.solve()

        # Assert
        assert solve.calls == ["R", "U"]
        assert result == Algorithm.from_str("R U")

    def test_invalid_cube_fails_validation_before_any_step_runs(self) -> None:
        """
        Tests that a cube which fails validation raises a ValueError before any step runs.

        :return: None
        """

        # Build an invalid cube
        cube = Cube(1)
        solve = _StubSolve(cube, ["R"])

        # Assert
        with pytest.raises(ValueError):
            solve.solve()
        assert solve.calls == []

    def test_returned_solution_has_no_rotations(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that rotations applied by a step are removed from the returned solution, with the
        moves after them rewritten in the pre-rotation orientation.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(3, "")
        solve = _StubSolve(cube, ["x R U R' U'"])
        result = solve.solve()

        # Assert
        assert result == Algorithm.from_str("R F R' F'")

    def test_reduction_runs_after_rotation_removal(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that the final reduction happens after rotation removal: `R x R'` can only cancel
        to an empty algorithm once the `x` between the two `R` moves has been removed and the
        second `R` rewritten in the pre-rotation orientation.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(3, "")
        solve = _StubSolve(cube, ["R x R'"])
        result = solve.solve()

        # Assert
        assert result == Algorithm([])

    def test_no_steps_on_a_solved_cube_returns_an_empty_algorithm(
        self, generate_cube: Callable[[int, str], Cube]
    ) -> None:
        """
        Tests that a subclass with no steps returns an empty algorithm when solving a solved
        cube.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(3, "")
        solve = _StubSolve(cube, [])
        result = solve.solve()

        # Assert
        assert result == Algorithm([])
