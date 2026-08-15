# Python imports
from typing import Callable

import pytest

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.cube_rotation.move import Move
from rubik_cube_solver.cube_rotation.rotator import Rotator
from rubik_cube_solver.enums.Direction import Direction
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.enums.Rotation import Rotation

# Moves used in the case tables below, named after the notation they represent
U: Move = Move(Layer.UP, Direction.CW, 1)
U2: Move = Move(Layer.UP, Direction.DOUBLE, 1)
D: Move = Move(Layer.DOWN, Direction.CW, 1)
R: Move = Move(Layer.RIGHT, Direction.CW, 1)
R_PRIME: Move = Move(Layer.RIGHT, Direction.CCW, 1)
RW_PRIME: Move = Move(Layer.RIGHT, Direction.CCW, 2)
FW2: Move = Move(Layer.FRONT, Direction.DOUBLE, 2)
FW2_3_LAYERS: Move = Move(Layer.FRONT, Direction.DOUBLE, 3)


class TestAlgorithmMoves:
    # fmt: off
    @pytest.mark.parametrize(
        "moves", [
            [],
            [U],
            [U, RW_PRIME],
        ]
    )
    # fmt: on
    def test_getter(
        self,
        generate_algorithm: Callable[[list[Move]], Algorithm],
        moves: list[Move],
    ) -> None:
        """
        Tests the moves getter of the Algorithm class.

        :param generate_algorithm: Fixture to generate an algorithm
        :param moves: The moves of the algorithm
        :return: None
        """

        # Mock the algorithm
        algorithm = generate_algorithm(moves)

        # Assert
        assert algorithm.moves == moves

    # fmt: off
    @pytest.mark.parametrize(
        "initial_moves, new_moves", [
            ([],  [U]),
            ([U], []),
            ([U], [RW_PRIME]),
        ]
    )
    # fmt: on
    def test_setter(
        self,
        generate_algorithm: Callable[[list[Move]], Algorithm],
        initial_moves: list[Move],
        new_moves: list[Move],
    ) -> None:
        """
        Tests the moves setter of the Algorithm class.

        :param generate_algorithm: Fixture to generate an algorithm
        :param initial_moves: The initial moves of the algorithm
        :param new_moves: The new moves to set on the algorithm
        :return: None
        """

        # Mock the algorithm
        algorithm = generate_algorithm(initial_moves)

        # Act
        algorithm.moves = new_moves

        # Assert
        assert algorithm.moves == new_moves


class TestAlgorithmStr:
    # fmt: off
    @pytest.mark.parametrize(
        "moves, algorithm_str", [
            ([],                              ""),
            ([U],                             "U"),
            ([U, R_PRIME],                    "U R'"),
            ([U, R_PRIME, FW2],               "U R' Fw2"),
            ([R, U2, RW_PRIME, FW2_3_LAYERS], "R U2 Rw' 3Fw2"),
        ]
    )
    # fmt: on
    def test_success(
        self,
        generate_algorithm: Callable[[list[Move]], Algorithm],
        moves: list[Move],
        algorithm_str: str,
    ) -> None:
        """
        Tests the string representation of the Algorithm class.

        :param generate_algorithm: Fixture to generate an algorithm
        :param moves: The moves of the algorithm
        :param algorithm_str: The expected string representation of the algorithm
        :return: None
        """

        # Mock the algorithm
        algorithm = generate_algorithm(moves)

        # Assert
        assert str(algorithm) == algorithm_str


class TestAlgorithmEq:
    # fmt: off
    @pytest.mark.parametrize(
        "moves, other_moves, expected", [
            ([],            [],            True),
            ([U],           [U],           True),
            ([U],           [D],           False),
            ([U],           [],            False),
            ([U, R_PRIME],  [U, R_PRIME],  True),
            ([U, R_PRIME],  [R_PRIME, U],  False),
        ]
    )
    # fmt: on
    def test_success(
        self,
        generate_algorithm: Callable[[list[Move]], Algorithm],
        moves: list[Move],
        other_moves: list[Move],
        expected: bool,
    ) -> None:
        """
        Tests the equality method of the Algorithm class.

        :param generate_algorithm: Fixture to generate an algorithm
        :param moves: The moves of the first algorithm
        :param other_moves: The moves of the second algorithm
        :param expected: The expected result of the equality comparison
        :return: None
        """

        # Mock the algorithms
        algorithm = generate_algorithm(moves)
        other_algorithm = generate_algorithm(other_moves)

        # Assert
        assert (algorithm == other_algorithm) == expected

    # fmt: off
    @pytest.mark.parametrize(
        "moves", [
            [],
            [U],
        ]
    )
    # fmt: on
    def test_different_type(
        self,
        generate_algorithm: Callable[[list[Move]], Algorithm],
        moves: list[Move],
    ) -> None:
        """
        Tests the equality method of the Algorithm class when compared to a different type.

        :param generate_algorithm: Fixture to generate an algorithm
        :param moves: The moves of the algorithm
        :return: None
        """

        # Mock the algorithm
        algorithm = generate_algorithm(moves)
        other_algorithm = "Not an Algorithm"

        # Assert
        assert algorithm != other_algorithm


class TestAlgorithmRemoveRotations:
    # fmt: off
    @pytest.mark.parametrize(
        "algorithm_string, expected_string", [
            ("",                     ""),
            ("R U R' U'",            "R U R' U'"),
            ("x",                    ""),
            ("x y z",                ""),
            ("x R U R' U'",          "R F R' F'"),
            ("x R U y R' U'",        "R F U' F'"),
            ("x2 R U",               "R D"),
            ("y' R U",               "F U"),
            ("z F L",                "F D"),
            ("R U x2 3Bw D",         "R U 3Fw U"),
            ("y' Rw2 3Fw'",          "Fw2 3Lw'"),
            ("R U x",                "R U"),
        ]
    )
    # fmt: on
    def test_success(self, algorithm_string: str, expected_string: str) -> None:
        """
        Tests that removing the rotations of an algorithm rewrites the following moves into the
        orientation the algorithm started from.

        :param algorithm_string: The string representation of the algorithm
        :param expected_string: The string representation of the expected rotation-free algorithm
        :return: None
        """

        # Mock the algorithm
        algorithm = Algorithm.from_str(algorithm_string)

        # Act
        algorithm.remove_rotations()

        # Assert
        assert algorithm == Algorithm.from_str(expected_string)

    # fmt: off
    @pytest.mark.parametrize(
        "algorithm_string", [
            "x R U R' U'",
            "x R U y R' U'",
            "z' y2 x' U L2 Fw",
        ]
    )
    # fmt: on
    def test_equivalent_to_the_original(
        self,
        generate_cube: Callable[[int], Cube],
        generate_rotator: Callable[[Cube], Rotator],
        algorithm_string: str,
    ) -> None:
        """
        Tests that the rotation-free algorithm leaves the cube in the same state as the original one,
        once the rotations the original performed are applied on top of it.

        :param generate_cube: Fixture to generate a cube
        :param generate_rotator: Fixture to generate a rotator
        :param algorithm_string: The string representation of the algorithm
        :return: None
        """

        # Mock the cubes
        original_cube = generate_cube(5)
        rotation_free_cube = generate_cube(5)

        # Mock the algorithms
        original = Algorithm.from_str(algorithm_string)
        rotation_free = Algorithm.from_str(algorithm_string)
        rotation_free.remove_rotations()

        # Act
        generate_rotator(original_cube).apply(original)
        rotation_free_rotator = generate_rotator(rotation_free_cube)
        rotation_free_rotator.apply(rotation_free)

        # Re-orient the second cube with the rotations that were removed
        for move in Algorithm.from_str(algorithm_string).moves:
            if isinstance(move.layer, Rotation):
                rotation_free_rotator.turn(move)

        # Assert
        assert original_cube.layers == rotation_free_cube.layers


class TestAlgorithmFromStr:
    # fmt: off
    @pytest.mark.parametrize(
        "algorithm_string, expected_moves", [
            ("",                []),
            ("   ",             []),
            ("U",               [U]),
            ("R  U\tR'",        [R, U, R_PRIME]),
            (" R U2 Rw' 3Fw2 ", [R, U2, RW_PRIME, FW2_3_LAYERS]),
        ]
    )
    # fmt: on
    def test_success(
        self,
        algorithm_string: str,
        expected_moves: list[Move],
    ) -> None:
        """
        Tests creating an Algorithm from string.

        :param algorithm_string: The string representation of the algorithm
        :param expected_moves: The expected moves of the algorithm
        :return: None
        """

        # Act
        algorithm = Algorithm.from_str(algorithm_string)

        # Assert
        assert algorithm.moves == expected_moves

    # fmt: off
    @pytest.mark.parametrize(
        "algorithm_string", [
            "",
            "U",
            "R U2 Rw' 3Fw2",
        ]
    )
    # fmt: on
    def test_round_trip(self, algorithm_string: str) -> None:
        """
        Tests that an algorithm string survives a from_str -> str round trip unchanged.

        :param algorithm_string: The string representation of the algorithm
        :return: None
        """

        # Act
        algorithm = Algorithm.from_str(algorithm_string)

        # Assert
        assert str(algorithm) == algorithm_string
        assert Algorithm.from_str(str(algorithm)) == algorithm

    # fmt: off
    @pytest.mark.parametrize(
        "algorithm_string, invalid_move", [
            ("U X",   "X"),
            ("U RR",  "RR"),
            ("R,U",   "R,U"),
        ]
    )
    # fmt: on
    def test_invalid_move(self, algorithm_string: str, invalid_move: str) -> None:
        """
        Tests that creating an Algorithm from a string with an invalid move token raises a ValueError.

        :param algorithm_string: The string representation of the algorithm
        :param invalid_move: The move token that cannot be parsed
        :return: None
        """

        # Assert
        with pytest.raises(ValueError, match=f"Couldn't parse move notation: {invalid_move}"):
            Algorithm.from_str(algorithm_string)
