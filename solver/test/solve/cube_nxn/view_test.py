# Python imports
from typing import Callable

import pytest

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.cube_rotation.orientation import Orientation
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.solve.cube_nxn.view import held_in_view, viewing_grip


class TestViewingGrip:
    # fmt: off
    @pytest.mark.parametrize(
        "target", [
            Layer.UP,
            Layer.FRONT,
            Layer.RIGHT,
        ]
    )
    # fmt: on
    def test_already_in_view(self, target: Layer) -> None:
        """
        Tests that a face already in view needs no whole-cube rotation to see it.

        :param target: The face to bring into view
        :return: None
        """

        # Assert
        assert viewing_grip(target) == Algorithm([])

    # fmt: off
    @pytest.mark.parametrize(
        "target, expected", [
            (Layer.LEFT, "y'"),
            (Layer.DOWN, "x"),
            (Layer.BACK, "x2"),
        ]
    )
    # fmt: on
    def test_hidden_face(self, target: Layer, expected: str) -> None:
        """
        Tests the docstring example: LEFT comes forward with `y'` and DOWN with `x`, and that BACK
        takes the shortest sequence reaching it, `x2`.

        :param target: The face to bring into view
        :param expected: The expected rotation, in standard notation
        :return: None
        """

        # Assert
        assert str(viewing_grip(target)) == expected

    # fmt: off
    @pytest.mark.parametrize(
        "target", [
            Layer.LEFT,
            Layer.DOWN,
            Layer.BACK,
        ]
    )
    # fmt: on
    def test_brings_the_face_to_front(self, target: Layer) -> None:
        """
        Tests that performing the returned rotation really does bring the target face to FRONT.

        :param target: The face to bring into view
        :return: None
        """

        # Act
        grip = viewing_grip(target)

        # Assert
        assert Orientation.from_moves(grip.moves).layers[Layer.FRONT] is target


class TestHeldInView:
    # fmt: off
    @pytest.mark.parametrize(
        "target", [
            Layer.UP,
            Layer.FRONT,
            Layer.RIGHT,
        ]
    )
    # fmt: on
    def test_target_already_in_view(self, target: Layer) -> None:
        """
        Tests that a target already in view returns the given algorithms unchanged.

        :param target: The face the work is done on
        :return: None
        """

        # Mock the moves
        moves = ["L U L'", "Dw R2 Dw' R2"]

        # Assert
        assert held_in_view(moves, target) == moves

    def test_worked_example(self) -> None:
        """
        Tests the docstring example: the white center's `Lw L'` fetch renamed to `Fw F'` and framed
        by the turn into view.

        :return: None
        """

        # Assert
        assert held_in_view(["Lw L'", "Dw R2 Dw' R2"], Layer.LEFT) == ["y'", "Fw F'", "Dw B2 Dw' B2", "y"]

    # fmt: off
    @pytest.mark.parametrize(
        "target", [
            Layer.LEFT,
            Layer.DOWN,
            Layer.BACK,
        ]
    )
    # fmt: on
    def test_hidden_target_frames_the_algorithms(self, target: Layer) -> None:
        """
        Tests that a hidden target's algorithms are framed by the grip into view and its inverse,
        with the algorithms renamed in between.

        :param target: The face the work is done on
        :return: None
        """

        # Act
        held = held_in_view(["L U L'"], target)
        grip = viewing_grip(target)

        # Assert
        assert held[0] == str(grip)
        assert held[-1] == str(grip.inverse())
        assert len(held) == 3

    # fmt: off
    @pytest.mark.parametrize(
        "target", [
            Layer.LEFT,
            Layer.DOWN,
            Layer.BACK,
        ]
    )
    # fmt: on
    def test_equivalent_to_the_original(self, generate_cube: Callable[[int, str], Cube], target: Layer) -> None:
        """
        Tests that holding a hidden target's algorithms in view does the same work as performing them
        directly: the cube ends up in the same state either way.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param target: The face the work is done on
        :return: None
        """

        # Mock the cubes
        moves = ["L U L'", "Dw R2 Dw' R2"]
        original = generate_cube(5, " ".join(moves))
        held = generate_cube(5, " ".join(held_in_view(moves, target)))

        # Assert
        assert original.layers == held.layers
