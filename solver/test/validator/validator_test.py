# Python imports
from unittest.mock import patch

import pytest

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.validator.validator import Validator


class TestValidatorValidate:
    def test_success_small_odd(self, validator: Validator) -> None:
        """
        Test that validate calls the correct check methods for a small odd sized cube (size 3).

        :param validator: Fixture of a Validator instance
        :return: None
        """

        cube = Cube(3)
        with (
            patch.object(validator, "_check_size") as mock_check_size,
            patch.object(validator, "_check_color_count") as mock_check_color_count,
            patch.object(validator, "_check_corner_validity") as mock_check_corner_validity,
            patch.object(validator, "_check_corner_orientation") as mock_check_corner_orientation,
            patch.object(validator, "_check_corner_chirality") as mock_check_corner_chirality,
            patch.object(validator, "_check_center_uniqueness") as mock_check_center_uniqueness,
            patch.object(validator, "_check_center_opposites") as mock_check_center_opposites,
            patch.object(validator, "_check_center_count_big") as mock_check_center_count_big,
            patch.object(validator, "_check_edge_validity") as mock_check_edge_validity,
            patch.object(validator, "_check_edge_flip_parity") as mock_check_edge_flip_parity,
            patch.object(validator, "_check_permutation_parity") as mock_check_permutation_parity,
            patch.object(validator, "_check_wing_edge_validity") as mock_check_wing_edge_validity,
        ):
            validator.validate(cube)
            mock_check_size.assert_called_once_with(cube)
            mock_check_color_count.assert_called_once_with(cube)
            mock_check_corner_validity.assert_called_once_with(cube)
            mock_check_corner_orientation.assert_called_once_with(cube)
            mock_check_corner_chirality.assert_called_once_with(cube)
            mock_check_center_uniqueness.assert_called_once_with(cube)
            mock_check_center_opposites.assert_called_once_with(cube)
            mock_check_center_count_big.assert_not_called()
            mock_check_edge_validity.assert_called_once_with(cube)
            mock_check_wing_edge_validity.assert_not_called()
            mock_check_edge_flip_parity.assert_called_once_with(cube)
            mock_check_permutation_parity.assert_called_once_with(cube)

    @pytest.mark.parametrize("cube_size", [5, 7])
    def test_success_big_odd(self, validator: Validator, cube_size: int) -> None:
        """
        Test that validate calls the correct check methods for a big odd sized cube (sizes 5, 7).

        :param validator: Fixture of a Validator instance
        :param cube_size: The size of the cube to validate
        :return: None
        """

        cube = Cube(cube_size)
        with (
            patch.object(validator, "_check_size") as mock_check_size,
            patch.object(validator, "_check_color_count") as mock_check_color_count,
            patch.object(validator, "_check_corner_validity") as mock_check_corner_validity,
            patch.object(validator, "_check_corner_orientation") as mock_check_corner_orientation,
            patch.object(validator, "_check_corner_chirality") as mock_check_corner_chirality,
            patch.object(validator, "_check_center_uniqueness") as mock_check_center_uniqueness,
            patch.object(validator, "_check_center_opposites") as mock_check_center_opposites,
            patch.object(validator, "_check_center_count_big") as mock_check_center_count_big,
            patch.object(validator, "_check_edge_validity") as mock_check_edge_validity,
            patch.object(validator, "_check_edge_flip_parity") as mock_check_edge_flip_parity,
            patch.object(validator, "_check_permutation_parity") as mock_check_permutation_parity,
            patch.object(validator, "_check_wing_edge_validity") as mock_check_wing_edge_validity,
        ):
            validator.validate(cube)
            mock_check_size.assert_called_once_with(cube)
            mock_check_color_count.assert_called_once_with(cube)
            mock_check_corner_validity.assert_called_once_with(cube)
            mock_check_corner_orientation.assert_called_once_with(cube)
            mock_check_corner_chirality.assert_called_once_with(cube)
            mock_check_center_uniqueness.assert_called_once_with(cube)
            mock_check_center_opposites.assert_called_once_with(cube)
            mock_check_center_count_big.assert_called_once_with(cube)
            mock_check_edge_validity.assert_called_once_with(cube)
            mock_check_wing_edge_validity.assert_called_once_with(cube)
            mock_check_edge_flip_parity.assert_called_once_with(cube)
            mock_check_permutation_parity.assert_called_once_with(cube)

    def test_success_small_even(self, validator: Validator) -> None:
        """
        Test that validate calls the correct check methods for a small even sized cube (size 2).

        :param validator: Fixture of a Validator instance
        :return: None
        """

        cube = Cube(2)
        with (
            patch.object(validator, "_check_size") as mock_check_size,
            patch.object(validator, "_check_color_count") as mock_check_color_count,
            patch.object(validator, "_check_corner_validity") as mock_check_corner_validity,
            patch.object(validator, "_check_corner_orientation") as mock_check_corner_orientation,
            patch.object(validator, "_check_corner_chirality") as mock_check_corner_chirality,
            patch.object(validator, "_check_center_uniqueness") as mock_check_center_uniqueness,
            patch.object(validator, "_check_center_opposites") as mock_check_center_opposites,
            patch.object(validator, "_check_center_count_big") as mock_check_center_count_big,
            patch.object(validator, "_check_edge_validity") as mock_check_edge_validity,
            patch.object(validator, "_check_edge_flip_parity") as mock_check_edge_flip_parity,
            patch.object(validator, "_check_permutation_parity") as mock_check_permutation_parity,
            patch.object(validator, "_check_wing_edge_validity") as mock_check_wing_edge_validity,
        ):
            validator.validate(cube)
            mock_check_size.assert_called_once_with(cube)
            mock_check_color_count.assert_called_once_with(cube)
            mock_check_corner_validity.assert_called_once_with(cube)
            mock_check_corner_orientation.assert_called_once_with(cube)
            mock_check_corner_chirality.assert_called_once_with(cube)
            mock_check_center_uniqueness.assert_not_called()
            mock_check_center_opposites.assert_not_called()
            mock_check_center_count_big.assert_not_called()
            mock_check_edge_validity.assert_not_called()
            mock_check_wing_edge_validity.assert_not_called()
            mock_check_edge_flip_parity.assert_not_called()
            mock_check_permutation_parity.assert_not_called()

    @pytest.mark.parametrize("cube_size", [4, 6])
    def test_success_big_even(self, validator: Validator, cube_size: int) -> None:
        """
        Test that validate calls the correct check methods for a big even sized cube (sizes 4, 6).

        :param validator: Fixture of a Validator instance
        :param cube_size: The size of the cube to validate
        :return: None
        """

        cube = Cube(cube_size)
        with (
            patch.object(validator, "_check_size") as mock_check_size,
            patch.object(validator, "_check_color_count") as mock_check_color_count,
            patch.object(validator, "_check_corner_validity") as mock_check_corner_validity,
            patch.object(validator, "_check_corner_orientation") as mock_check_corner_orientation,
            patch.object(validator, "_check_corner_chirality") as mock_check_corner_chirality,
            patch.object(validator, "_check_center_uniqueness") as mock_check_center_uniqueness,
            patch.object(validator, "_check_center_opposites") as mock_check_center_opposites,
            patch.object(validator, "_check_center_count_big") as mock_check_center_count_big,
            patch.object(validator, "_check_edge_validity") as mock_check_edge_validity,
            patch.object(validator, "_check_edge_flip_parity") as mock_check_edge_flip_parity,
            patch.object(validator, "_check_permutation_parity") as mock_check_permutation_parity,
            patch.object(validator, "_check_wing_edge_validity") as mock_check_wing_edge_validity,
        ):
            validator.validate(cube)
            mock_check_size.assert_called_once_with(cube)
            mock_check_color_count.assert_called_once_with(cube)
            mock_check_corner_validity.assert_called_once_with(cube)
            mock_check_corner_orientation.assert_called_once_with(cube)
            mock_check_corner_chirality.assert_called_once_with(cube)
            mock_check_center_uniqueness.assert_not_called()
            mock_check_center_opposites.assert_not_called()
            mock_check_center_count_big.assert_called_once_with(cube)
            mock_check_edge_validity.assert_not_called()
            mock_check_wing_edge_validity.assert_called_once_with(cube)
            mock_check_edge_flip_parity.assert_not_called()
            mock_check_permutation_parity.assert_not_called()


class TestValidatorCheckSize:
    @pytest.mark.parametrize("cube_size", [2, 3, 4, 5])
    def test_success(self, validator: Validator, cube_size: int) -> None:
        """
        Test that _check_size does not raise for valid cube sizes.

        :param validator: Fixture of a Validator instance
        :param cube_size: The size of the cube to check
        :return: None
        """

        cube = Cube(cube_size)
        validator._check_size(cube)

    @pytest.mark.parametrize("cube_size", [1, 0, -1])
    def test_exception(self, validator: Validator, cube_size: int) -> None:
        """
        Test that _check_size raises ValueError for cube sizes less than 2.

        :param validator: Fixture of a Validator instance
        :param cube_size: The invalid cube size to check
        :return: None
        """

        cube = Cube(size=cube_size)
        with pytest.raises(ValueError, match="Cube size must be at least 2."):
            validator._check_size(cube)


class TestValidatorCheckColorCount:
    @pytest.mark.parametrize("cube_size", [2, 3, 4, 5])
    def test_success(self, validator: Validator, cube_size: int) -> None:
        """
        Test that _check_color_count does not raise for a solved cube of any valid size.

        :param validator: Fixture of a Validator instance
        :param cube_size: The size of the cube to check
        :return: None
        """

        cube = Cube(cube_size)
        validator._check_color_count(cube)

    def test_exception_wrong_count(self, validator: Validator) -> None:
        """
        Test that _check_color_count raises ValueError when WHITE appears 5 times and YELLOW 3 times on a 2x2 cube.

        :param validator: Fixture of a Validator instance
        :return: None
        """

        # fmt: off
        cube = Cube(
            size=2,
            layers={
                Layer.UP:    [Color.WHITE,  Color.WHITE,
                              Color.WHITE,  Color.WHITE],
                Layer.DOWN:  [Color.WHITE,  Color.YELLOW,
                              Color.YELLOW, Color.YELLOW],
                Layer.LEFT:  [Color.ORANGE, Color.ORANGE,
                              Color.ORANGE, Color.ORANGE],
                Layer.RIGHT: [Color.RED,    Color.RED,
                              Color.RED,    Color.RED],
                Layer.FRONT: [Color.GREEN,  Color.GREEN,
                              Color.GREEN,  Color.GREEN],
                Layer.BACK:  [Color.BLUE,   Color.BLUE,
                              Color.BLUE,   Color.BLUE],
            }
        )
        # fmt: on
        with pytest.raises(ValueError, match=r"Invalid color count for WHITE: expected 4, got 5\."):
            validator._check_color_count(cube)

    def test_exception_missing_color(self, validator: Validator) -> None:
        """
        Test that _check_color_count raises ValueError when one color is completely missing on a 3x3 cube.

        :param validator: Fixture of a Validator instance
        :return: None
        """

        # fmt: off
        cube = Cube(
            size=3,
            layers={
                Layer.UP:    [Color.WHITE] * 9,
                Layer.DOWN:  [Color.YELLOW] * 9,
                Layer.LEFT:  [Color.ORANGE] * 9,
                Layer.RIGHT: [Color.RED] * 9,
                Layer.FRONT: [Color.GREEN] * 9,
                Layer.BACK:  [Color.GREEN] * 9,
            }
        )
        # fmt: on
        with pytest.raises(ValueError, match=r"Invalid color count for GREEN: expected 9, got 18\."):
            validator._check_color_count(cube)


class TestValidatorCheckCornerValidity:
    def test_success(self, validator: Validator) -> None:
        """
        Test that _check_corner_validity does not raise when all 8 corners are valid and distinct.

        :param validator: Fixture of a Validator instance
        :return: None
        """

        cube = Cube(3)
        corners = [
            (Color.WHITE, Color.GREEN, Color.ORANGE),  # UFL
            (Color.WHITE, Color.RED, Color.GREEN),  # UFR
            (Color.WHITE, Color.ORANGE, Color.BLUE),  # UBL
            (Color.WHITE, Color.BLUE, Color.RED),  # UBR
            (Color.YELLOW, Color.ORANGE, Color.GREEN),  # DFL
            (Color.YELLOW, Color.GREEN, Color.RED),  # DFR
            (Color.YELLOW, Color.BLUE, Color.ORANGE),  # DBL
            (Color.YELLOW, Color.RED, Color.BLUE),  # DBR
        ]
        with patch("rubik_cube_solver.validator.validator.get_corners", return_value=corners):
            validator._check_corner_validity(cube)

    def test_exception_invalid_corner(self, validator: Validator) -> None:
        """
        Test that _check_corner_validity raises ValueError when one corner has an impossible color combination.

        :param validator: Fixture of a Validator instance
        :return: None
        """

        cube = Cube(3)
        # UBL has {WHITE, WHITE, BLUE} — two of the same color, invalid corner
        corners = [
            (Color.WHITE, Color.GREEN, Color.ORANGE),
            (Color.WHITE, Color.RED, Color.GREEN),
            (Color.WHITE, Color.WHITE, Color.BLUE),  # invalid: frozenset has only 2 distinct colors
            (Color.WHITE, Color.BLUE, Color.RED),
            (Color.YELLOW, Color.ORANGE, Color.GREEN),
            (Color.YELLOW, Color.GREEN, Color.RED),
            (Color.YELLOW, Color.BLUE, Color.ORANGE),
            (Color.YELLOW, Color.RED, Color.BLUE),
        ]
        with patch("rubik_cube_solver.validator.validator.get_corners", return_value=corners):
            with pytest.raises(ValueError, match="Invalid corner piece"):
                validator._check_corner_validity(cube)

    def test_exception_duplicate_corner(self, validator: Validator) -> None:
        """
        Test that _check_corner_validity raises ValueError when two corners have the same color set.

        :param validator: Fixture of a Validator instance
        :return: None
        """

        cube = Cube(3)
        # UBL is a duplicate of UFL — both have {WHITE, GREEN, ORANGE}
        corners = [
            (Color.WHITE, Color.GREEN, Color.ORANGE),  # UFL
            (Color.WHITE, Color.RED, Color.GREEN),
            (Color.WHITE, Color.GREEN, Color.ORANGE),  # duplicate of UFL
            (Color.WHITE, Color.BLUE, Color.RED),
            (Color.YELLOW, Color.ORANGE, Color.GREEN),
            (Color.YELLOW, Color.GREEN, Color.RED),
            (Color.YELLOW, Color.BLUE, Color.ORANGE),
            (Color.YELLOW, Color.RED, Color.BLUE),
        ]
        with patch("rubik_cube_solver.validator.validator.get_corners", return_value=corners):
            with pytest.raises(ValueError, match="Duplicate corner piece"):
                validator._check_corner_validity(cube)


class TestValidatorCheckCornerOrientation:
    def test_success(self, validator: Validator) -> None:
        """
        Test that _check_corner_orientation does not raise when all corners have orientation 0 (total = 0).

        :param validator: Fixture of a Validator instance
        :return: None
        """

        cube = Cube(3)
        # All UP/DOWN colors in position 0 → all orientations 0 → total = 0
        corners = [
            (Color.WHITE, Color.GREEN, Color.ORANGE),
            (Color.WHITE, Color.RED, Color.GREEN),
            (Color.WHITE, Color.ORANGE, Color.BLUE),
            (Color.WHITE, Color.BLUE, Color.RED),
            (Color.YELLOW, Color.ORANGE, Color.GREEN),
            (Color.YELLOW, Color.GREEN, Color.RED),
            (Color.YELLOW, Color.BLUE, Color.ORANGE),
            (Color.YELLOW, Color.RED, Color.BLUE),
        ]
        with patch("rubik_cube_solver.validator.validator.get_corners", return_value=corners):
            validator._check_corner_orientation(cube)

    # fmt: off
    @pytest.mark.parametrize(
        "corners, exception",
        [
            (
                [
                    (Color.GREEN, Color.WHITE, Color.ORANGE),  # UFL twisted: WHITE at position 1, orientation 1
                    (Color.WHITE, Color.RED, Color.GREEN),
                    (Color.WHITE, Color.ORANGE, Color.BLUE),
                    (Color.WHITE, Color.BLUE, Color.RED),
                    (Color.YELLOW, Color.ORANGE, Color.GREEN),
                    (Color.YELLOW, Color.GREEN, Color.RED),
                    (Color.YELLOW, Color.BLUE, Color.ORANGE),
                    (Color.YELLOW, Color.RED, Color.BLUE),
                ],
                "Invalid corner orientation parity",
            ),
            (
                [
                    (Color.ORANGE, Color.GREEN, Color.WHITE),  # UFL twisted: WHITE at position 2, orientation 2
                    (Color.WHITE, Color.RED, Color.GREEN),
                    (Color.WHITE, Color.ORANGE, Color.BLUE),
                    (Color.WHITE, Color.BLUE, Color.RED),
                    (Color.YELLOW, Color.ORANGE, Color.GREEN),
                    (Color.YELLOW, Color.GREEN, Color.RED),
                    (Color.YELLOW, Color.BLUE, Color.ORANGE),
                    (Color.YELLOW, Color.RED, Color.BLUE),
                ],
                "Invalid corner orientation parity",
            ),
            (
                [
                    (Color.ORANGE, Color.GREEN, Color.ORANGE),  # UFL doesn't contain WHITE / YELLOW
                    (Color.WHITE, Color.RED, Color.GREEN),
                    (Color.WHITE, Color.ORANGE, Color.BLUE),
                    (Color.WHITE, Color.BLUE, Color.RED),
                    (Color.YELLOW, Color.ORANGE, Color.GREEN),
                    (Color.YELLOW, Color.GREEN, Color.RED),
                    (Color.YELLOW, Color.BLUE, Color.ORANGE),
                    (Color.YELLOW, Color.RED, Color.BLUE),
                ],
                "Corner has no UP/DOWN color",
            )
        ]
    )
    # fmt: on
    def test_exception(self, validator: Validator, corners: list[tuple[Color, Color, Color]], exception: str) -> None:
        """
        Test that _check_corner_orientation raises ValueError when orientation parity is broken.

        :param validator: Fixture of a Validator instance
        :param corners: Corners of the cube for testing
        :param exception: Expected exception
        :return: None
        """

        cube = Cube(3)
        with patch("rubik_cube_solver.validator.validator.get_corners", return_value=corners):
            with pytest.raises(ValueError, match=exception):
                validator._check_corner_orientation(cube)


class TestValidatorCheckCornerChirality:
    def test_success(self, validator: Validator) -> None:
        """
        Test that _check_corner_chirality does not raise when all corners are in canonical CW cyclic order.

        :param validator: Fixture of a Validator instance
        :return: None
        """

        cube = Cube(3)
        # Each tuple matches the canonical CW sequence (or a valid cyclic rotation thereof)
        corners = [
            (Color.WHITE, Color.GREEN, Color.ORANGE),  # canonical for {W,G,O}
            (Color.WHITE, Color.RED, Color.GREEN),  # canonical for {W,G,R}
            (Color.WHITE, Color.ORANGE, Color.BLUE),  # canonical for {W,B,O}
            (Color.WHITE, Color.BLUE, Color.RED),  # canonical for {W,B,R}
            (Color.YELLOW, Color.ORANGE, Color.GREEN),  # canonical for {Y,G,O}
            (Color.YELLOW, Color.GREEN, Color.RED),  # canonical for {Y,G,R}
            (Color.YELLOW, Color.BLUE, Color.ORANGE),  # canonical for {Y,B,O}
            (Color.YELLOW, Color.RED, Color.BLUE),  # canonical for {Y,B,R}
        ]
        with patch("rubik_cube_solver.validator.validator.get_corners", return_value=corners):
            validator._check_corner_chirality(cube)

    def test_exception(self, validator: Validator) -> None:
        """
        Test that _check_corner_chirality raises ValueError when a corner's stickers are in the wrong cyclic order.

        :param validator: Fixture of a Validator instance
        :return: None
        """

        cube = Cube(3)
        # UFL has (WHITE, ORANGE, GREEN) — this is the reverse cyclic order of canonical (WHITE, GREEN, ORANGE)
        corners = [
            (Color.WHITE, Color.ORANGE, Color.GREEN),  # reversed chirality for {W,G,O}
            (Color.WHITE, Color.RED, Color.GREEN),
            (Color.WHITE, Color.ORANGE, Color.BLUE),
            (Color.WHITE, Color.BLUE, Color.RED),
            (Color.YELLOW, Color.ORANGE, Color.GREEN),
            (Color.YELLOW, Color.GREEN, Color.RED),
            (Color.YELLOW, Color.BLUE, Color.ORANGE),
            (Color.YELLOW, Color.RED, Color.BLUE),
        ]
        with patch("rubik_cube_solver.validator.validator.get_corners", return_value=corners):
            with pytest.raises(ValueError, match="Invalid corner chirality"):
                validator._check_corner_chirality(cube)


class TestValidatorCheckCenterUniqueness:
    @pytest.mark.parametrize("cube_size", [3, 5])
    def test_success(self, validator: Validator, cube_size: int) -> None:
        """
        Test that _check_center_uniqueness does not raise for a solved odd sized cube.

        :param validator: Fixture of a Validator instance
        :param cube_size: The size of the cube to validate
        :return: None
        """

        cube = Cube(cube_size)
        validator._check_center_uniqueness(cube)

    @pytest.mark.parametrize(
        "cube_size, layers",
        [
            (
                3,
                {
                    Layer.UP: [Color.WHITE] * 9,
                    Layer.DOWN: [Color.WHITE] * 9,  # duplicate of UP center color
                    Layer.LEFT: [Color.ORANGE] * 9,
                    Layer.RIGHT: [Color.RED] * 9,
                    Layer.FRONT: [Color.GREEN] * 9,
                    Layer.BACK: [Color.BLUE] * 9,
                },
            ),
            (
                5,
                {
                    Layer.UP: [Color.WHITE] * 25,
                    Layer.DOWN: [Color.YELLOW] * 25,
                    Layer.LEFT: [Color.ORANGE] * 25,
                    Layer.RIGHT: [Color.ORANGE] * 25,  # duplicate of LEFT center color
                    Layer.FRONT: [Color.GREEN] * 25,
                    Layer.BACK: [Color.BLUE] * 25,
                },
            ),
        ],
    )
    def test_exception_duplicate_center(
        self, validator: Validator, cube_size: int, layers: dict[Layer, list[Color]]
    ) -> None:
        """
        Test that _check_center_uniqueness raises ValueError when two faces share the same center color.

        :param validator: Fixture of a Validator instance
        :param cube_size: The size of the cube to validate
        :param layers: Layer configuration for the cube with duplicate center colors
        :return: None
        """

        cube = Cube(cube_size, layers)
        with pytest.raises(ValueError, match="Duplicate center piece"):
            validator._check_center_uniqueness(cube)


class TestValidatorCheckCenterOpposites:
    @pytest.mark.parametrize("cube_size", [3, 5])
    def test_success(self, validator: Validator, cube_size: int) -> None:
        """
        Test that _check_center_opposites does not raise for a solved 3x3 cube.

        :param validator: Fixture of a Validator instance
        :param cube_size: The size of the cube to validate
        :return: None
        """

        cube = Cube(cube_size)
        validator._check_center_opposites(cube)

    @pytest.mark.parametrize(
        "cube_size, layers",
        [
            (
                3,
                {
                    Layer.UP: [Color.WHITE] * 9,
                    Layer.DOWN: [Color.ORANGE] * 9,  # incorrect opposite color of UP, must be YELLOW
                    Layer.LEFT: [Color.YELLOW] * 9,  # incorrect opposite color of RIGHT, must be ORANGE
                    Layer.RIGHT: [Color.RED] * 9,
                    Layer.FRONT: [Color.GREEN] * 9,
                    Layer.BACK: [Color.BLUE] * 9,
                },
            ),
            (
                5,
                {
                    Layer.UP: [Color.WHITE] * 25,
                    Layer.DOWN: [Color.YELLOW] * 25,
                    Layer.LEFT: [Color.ORANGE] * 25,
                    Layer.RIGHT: [Color.GREEN] * 25,  # incorrect opposite color of LEFT, must be RED
                    Layer.FRONT: [Color.RED] * 25,  # incorrect opposite color of BACK, must be GREEN
                    Layer.BACK: [Color.BLUE] * 25,
                },
            ),
        ],
    )
    def test_exception_incorrect_opposite(
        self, validator: Validator, cube_size: int, layers: dict[Layer, list[Color]]
    ) -> None:
        """
        Test that _check_center_opposites raises ValueError when opposite color is wrong.

        :param validator: Fixture of a Validator instance
        :param cube_size: The size of the cube to validate
        :param layers: Layer configuration for the cube with incorrect opposite colors
        """

        cube = Cube(cube_size, layers)
        with pytest.raises(ValueError, match="Invalid opposite color"):
            validator._check_center_opposites(cube)


class TestValidatorCheckCenterCountBig:
    @pytest.mark.parametrize("cube_size", [4, 5, 6, 7])
    def test_success(self, validator: Validator, cube_size: int) -> None:
        """
        Test that _check_center_count_even does not raise for a solved big cube.

        :param validator: Fixture of a Validator instance
        :param cube_size: The size of the cube to validate
        :return: None
        """

        cube = Cube(cube_size)
        validator._check_center_count_big(cube)

    @pytest.mark.parametrize(
        "cube_size, layers",
        [
            (
                4,
                {
                    Layer.UP: [Color.WHITE] * 5 + [Color.YELLOW] + [Color.WHITE] * 10,
                    Layer.DOWN: [Color.YELLOW] * 16,
                    Layer.LEFT: [Color.ORANGE] * 16,
                    Layer.RIGHT: [Color.RED] * 16,
                    Layer.FRONT: [Color.GREEN] * 16,
                    Layer.BACK: [Color.BLUE] * 16,
                },
            ),
            (
                5,
                {
                    Layer.UP: [Color.WHITE] * 6 + [Color.YELLOW] + [Color.WHITE] * 18,
                    Layer.DOWN: [Color.YELLOW] * 25,
                    Layer.LEFT: [Color.ORANGE] * 25,
                    Layer.RIGHT: [Color.RED] * 25,
                    Layer.FRONT: [Color.GREEN] * 25,
                    Layer.BACK: [Color.BLUE] * 25,
                },
            ),
            (
                6,
                {
                    Layer.UP: [Color.WHITE] * 7 + [Color.YELLOW] + [Color.WHITE] * 28,
                    Layer.DOWN: [Color.YELLOW] * 36,
                    Layer.LEFT: [Color.ORANGE] * 36,
                    Layer.RIGHT: [Color.RED] * 36,
                    Layer.FRONT: [Color.GREEN] * 36,
                    Layer.BACK: [Color.BLUE] * 36,
                },
            ),
            (
                7,
                {
                    Layer.UP: [Color.WHITE] * 8 + [Color.YELLOW] + [Color.WHITE] * 40,
                    Layer.DOWN: [Color.YELLOW] * 49,
                    Layer.LEFT: [Color.ORANGE] * 49,
                    Layer.RIGHT: [Color.RED] * 49,
                    Layer.FRONT: [Color.GREEN] * 49,
                    Layer.BACK: [Color.BLUE] * 49,
                },
            ),
        ],
    )
    def test_exception_wrong_count(
        self, validator: Validator, cube_size: int, layers: dict[Layer, list[Color]]
    ) -> None:
        """
        Test that _check_center_count_even raises ValueError when a center type has wrong count.

        :param validator: Fixture of a Validator instance
        :return: None
        """

        cube = Cube(cube_size, layers)
        with pytest.raises(ValueError, match="Invalid center piece count"):
            validator._check_center_count_big(cube)


class TestValidatorCheckEdgeValidity:
    @pytest.mark.parametrize("cube_size", [3, 5])
    def test_success(self, validator: Validator, cube_size: int) -> None:
        """
        Test that _check_edge_validity does not raise when all 12 edges are valid and distinct.

        :param validator: Fixture of a Validator instance
        :param cube_size: The size of the cube to validate
        :return: None
        """

        cube = Cube(cube_size)
        # fmt: off
        edges = [
            (Color.WHITE,  Color.GREEN),
            (Color.WHITE,  Color.BLUE),
            (Color.WHITE,  Color.ORANGE),
            (Color.WHITE,  Color.RED),
            (Color.YELLOW, Color.GREEN),
            (Color.YELLOW, Color.BLUE),
            (Color.YELLOW, Color.ORANGE),
            (Color.YELLOW, Color.RED),
            (Color.GREEN,  Color.ORANGE),
            (Color.GREEN,  Color.RED),
            (Color.BLUE,   Color.ORANGE),
            (Color.BLUE,   Color.RED),
        ]
        # fmt: on
        with patch("rubik_cube_solver.validator.validator.get_edges", return_value=edges):
            validator._check_edge_validity(cube)

    @pytest.mark.parametrize("cube_size", [3, 5])
    def test_exception_invalid_edge(self, validator: Validator, cube_size: int) -> None:
        """
        Test that _check_edge_validity raises ValueError when one edge has an impossible color combination.

        :param validator: Fixture of a Validator instance
        :return: None
        """

        cube = Cube(cube_size)
        # fmt: off
        edges = [
            (Color.WHITE,  Color.YELLOW),  # invalid: opposite faces cannot share an edge
            (Color.WHITE,  Color.BLUE),
            (Color.WHITE,  Color.ORANGE),
            (Color.WHITE,  Color.RED),
            (Color.YELLOW, Color.GREEN),
            (Color.YELLOW, Color.BLUE),
            (Color.YELLOW, Color.ORANGE),
            (Color.YELLOW, Color.RED),
            (Color.GREEN,  Color.ORANGE),
            (Color.GREEN,  Color.RED),
            (Color.BLUE,   Color.ORANGE),
            (Color.BLUE,   Color.RED),
        ]
        # fmt: on
        with patch("rubik_cube_solver.validator.validator.get_edges", return_value=edges):
            with pytest.raises(ValueError, match="Invalid edge piece"):
                validator._check_edge_validity(cube)

    @pytest.mark.parametrize("cube_size", [3, 5])
    def test_exception_duplicate_edge(self, validator: Validator, cube_size: int) -> None:
        """
        Test that _check_edge_validity raises ValueError when two edges have the same color set.

        :param validator: Fixture of a Validator instance
        :param cube_size: The size of the cube to validate
        :return: None
        """

        cube = Cube(cube_size)
        # fmt: off
        edges = [
            (Color.WHITE,  Color.GREEN),
            (Color.WHITE,  Color.GREEN),  # duplicate of first edge
            (Color.WHITE,  Color.ORANGE),
            (Color.WHITE,  Color.RED),
            (Color.YELLOW, Color.GREEN),
            (Color.YELLOW, Color.BLUE),
            (Color.YELLOW, Color.ORANGE),
            (Color.YELLOW, Color.RED),
            (Color.GREEN,  Color.ORANGE),
            (Color.GREEN,  Color.RED),
            (Color.BLUE,   Color.ORANGE),
            (Color.BLUE,   Color.RED),
        ]
        # fmt: on
        with patch("rubik_cube_solver.validator.validator.get_edges", return_value=edges):
            with pytest.raises(ValueError, match="Duplicate edge piece"):
                validator._check_edge_validity(cube)


class TestValidatorCheckWingEdgeValidity:
    @pytest.mark.parametrize("cube_size", [4, 5, 6, 7])
    def test_success(self, validator: Validator, cube_size: int) -> None:
        """
        Test that _check_wing_edge_validity does not raise for a solved big cube.

        :param validator: Fixture of a Validator instance
        :param cube_size: The size of the cube to validate
        :return: None
        """

        cube = Cube(4)
        validator._check_wing_edge_validity(cube)

    def test_exception_invalid_wing_edge_piece(self, validator: Validator) -> None:
        """
        Test that _check_wing_edge_validity raises ValueError when a wing edge doesn't contain the expected colors.

        :param validator: Fixture of a Validator instance
        :return: None
        """

        cube = Cube(4)
        # fmt: off
        wing_edges = [
            (1, Color.WHITE,  Color.YELLOW),  # invalid: opposite faces cannot share a wing edge
            (1, Color.WHITE,  Color.RED),
            (1, Color.WHITE,  Color.GREEN),
            (1, Color.WHITE,  Color.BLUE),
            (1, Color.YELLOW, Color.ORANGE),
            (1, Color.YELLOW, Color.RED),
            (1, Color.YELLOW, Color.GREEN),
            (1, Color.YELLOW, Color.BLUE),
            (1, Color.ORANGE, Color.WHITE),
            (1, Color.ORANGE, Color.YELLOW),
            (1, Color.ORANGE, Color.GREEN),
            (1, Color.ORANGE, Color.BLUE),
            (1, Color.RED,    Color.WHITE),
            (1, Color.RED,    Color.YELLOW),
            (1, Color.RED,    Color.GREEN),
            (1, Color.RED,    Color.BLUE),
            (1, Color.GREEN,  Color.WHITE),
            (1, Color.GREEN,  Color.YELLOW),
            (1, Color.GREEN,  Color.ORANGE),
            (1, Color.GREEN,  Color.RED),
            (1, Color.BLUE,   Color.WHITE),
            (1, Color.BLUE,   Color.YELLOW),
            (1, Color.BLUE,   Color.ORANGE),
            (1, Color.BLUE,   Color.RED),
        ]
        # fmt: on
        with patch("rubik_cube_solver.validator.validator.get_wing_edges", return_value=wing_edges):
            with pytest.raises(ValueError, match="Invalid wing edge piece"):
                validator._check_wing_edge_validity(cube)

    def test_exception_duplicate_wing_edge(self, validator: Validator) -> None:
        """
        Test that _check_wing_edge_validity raises ValueError when a directed wing edge type is duplicated.

        :param validator: Fixture of a Validator instance
        :return: None
        """

        cube = Cube(4)
        # fmt: off
        wing_edges = [
            (1, Color.WHITE,  Color.ORANGE),  # duplicate wing edge
            (1, Color.WHITE,  Color.RED),
            (1, Color.WHITE,  Color.GREEN),
            (1, Color.WHITE,  Color.BLUE),
            (1, Color.YELLOW, Color.ORANGE),
            (1, Color.YELLOW, Color.RED),
            (1, Color.YELLOW, Color.GREEN),
            (1, Color.YELLOW, Color.BLUE),
            (1, Color.WHITE,  Color.ORANGE),  # duplicate wing edge
            (1, Color.ORANGE, Color.YELLOW),
            (1, Color.ORANGE, Color.GREEN),
            (1, Color.ORANGE, Color.BLUE),
            (1, Color.RED,    Color.WHITE),
            (1, Color.RED,    Color.YELLOW),
            (1, Color.RED,    Color.GREEN),
            (1, Color.RED,    Color.BLUE),
            (1, Color.GREEN,  Color.WHITE),
            (1, Color.GREEN,  Color.YELLOW),
            (1, Color.GREEN,  Color.ORANGE),
            (1, Color.GREEN,  Color.RED),
            (1, Color.BLUE,   Color.WHITE),
            (1, Color.BLUE,   Color.YELLOW),
            (1, Color.BLUE,   Color.ORANGE),
            (1, Color.BLUE,   Color.RED),
        ]
        # fmt: on
        with patch("rubik_cube_solver.validator.validator.get_wing_edges", return_value=wing_edges):
            with pytest.raises(ValueError, match="Duplicate wing edge piece"):
                validator._check_wing_edge_validity(cube)


class TestValidatorCheckEdgeFlipParity:
    @pytest.mark.parametrize("cube_size", [3, 5])
    def test_success(self, validator: Validator, cube_size: int) -> None:
        """
        Test that _check_edge_flip_parity does not raise when all 12 edges are in oriented position.

        :param validator: Fixture of a Validator instance
        :param cube_size: The size of the cube to validate
        :return: None
        """

        cube = Cube(cube_size)
        # fmt: off
        edges = [
            (Color.WHITE,  Color.GREEN),
            (Color.WHITE,  Color.BLUE),
            (Color.WHITE,  Color.ORANGE),
            (Color.WHITE,  Color.RED),
            (Color.YELLOW, Color.GREEN),
            (Color.YELLOW, Color.BLUE),
            (Color.YELLOW, Color.ORANGE),
            (Color.YELLOW, Color.RED),
            (Color.GREEN,  Color.ORANGE),
            (Color.GREEN,  Color.RED),
            (Color.BLUE,   Color.ORANGE),
            (Color.BLUE,   Color.RED),
        ]
        # fmt: on
        with patch("rubik_cube_solver.validator.validator.get_edges", return_value=edges):
            validator._check_edge_flip_parity(cube)

    @pytest.mark.parametrize("cube_size", [3, 5])
    def test_success_six_flipped(self, validator: Validator, cube_size: int) -> None:
        """
        Test that _check_edge_flip_parity does not raise when 6 edges are flipped.
        """

        cube = Cube(cube_size)
        # fmt: off
        edges = [
            (Color.WHITE,  Color.GREEN),
            (Color.BLUE,   Color.WHITE),   # flipped UB edge
            (Color.WHITE,  Color.ORANGE),
            (Color.RED,    Color.WHITE),   # flipped UR edge
            (Color.YELLOW, Color.GREEN),
            (Color.BLUE,   Color.YELLOW),  # flipped DB edge
            (Color.YELLOW, Color.ORANGE),
            (Color.RED,    Color.YELLOW),  # flipped DR edge
            (Color.GREEN,  Color.ORANGE),
            (Color.RED,    Color.GREEN),   # flipped FR edge
            (Color.BLUE,   Color.ORANGE),
            (Color.RED,    Color.BLUE),    # flipped BR edge
        ]
        # fmt: on
        with patch("rubik_cube_solver.validator.validator.get_edges", return_value=edges):
            validator._check_edge_flip_parity(cube)

    @pytest.mark.parametrize("cube_size", [3, 5])
    def test_exception_one_flipped(self, validator: Validator, cube_size: int) -> None:
        """
        Test that _check_edge_flip_parity raises ValueError when 1 edge is flipped.

        :param validator: Fixture of a Validator instance
        :param cube_size: The size of the cube to validate
        :return: None
        """

        cube = Cube(cube_size)
        # fmt: off
        edges = [
            (Color.GREEN,  Color.WHITE),  # flipped UF edge
            (Color.WHITE,  Color.BLUE),
            (Color.WHITE,  Color.ORANGE),
            (Color.WHITE,  Color.RED),
            (Color.YELLOW, Color.GREEN),
            (Color.YELLOW, Color.BLUE),
            (Color.YELLOW, Color.ORANGE),
            (Color.YELLOW, Color.RED),
            (Color.GREEN,  Color.ORANGE),
            (Color.GREEN,  Color.RED),
            (Color.BLUE,   Color.ORANGE),
            (Color.BLUE,   Color.RED),
        ]
        # fmt: on
        with patch("rubik_cube_solver.validator.validator.get_edges", return_value=edges):
            with pytest.raises(ValueError, match="Invalid edge flip parity"):
                validator._check_edge_flip_parity(cube)

    @pytest.mark.parametrize("cube_size", [3, 5])
    def test_exception_seven_flipped(self, validator: Validator, cube_size: int) -> None:
        """
        Test that _check_edge_flip_parity raises ValueError when 7 edges are flipped.

        :param validator: Fixture of a Validator instance
        :param cube_size: The size of the cube to validate
        :return: None
        """

        cube = Cube(cube_size)
        # fmt: off
        edges = [
            (Color.GREEN,  Color.WHITE),   # flipped UF edge
            (Color.BLUE,   Color.WHITE),   # flipped UB edge
            (Color.WHITE,  Color.ORANGE),
            (Color.RED,    Color.WHITE),   # flipped UR edge
            (Color.YELLOW, Color.GREEN),
            (Color.BLUE,   Color.YELLOW),  # flipped DB edge
            (Color.YELLOW, Color.ORANGE),
            (Color.RED,    Color.YELLOW),  # flipped DR edge
            (Color.GREEN,  Color.ORANGE),
            (Color.RED,    Color.GREEN),   # flipped FR edge
            (Color.BLUE,   Color.ORANGE),
            (Color.RED,    Color.BLUE),    # flipped BR edge
        ]
        # fmt: on
        with patch("rubik_cube_solver.validator.validator.get_edges", return_value=edges):
            with pytest.raises(ValueError, match="Invalid edge flip parity"):
                validator._check_edge_flip_parity(cube)


class TestValidatorCheckPermutationParity:
    @pytest.mark.parametrize("cube_size", [3, 5])
    def test_success(self, validator: Validator, cube_size: int) -> None:
        """
        Test that _check_permutation_parity does not raise when corners and edges are both in solved order (both even).

        :param validator: Fixture of a Validator instance
        :param cube_size: The size of the cube to validate
        :return: None
        """

        cube = Cube(cube_size)
        # fmt: off
        corners = [
            (Color.WHITE,  Color.GREEN,  Color.ORANGE),
            (Color.WHITE,  Color.RED,    Color.GREEN),
            (Color.WHITE,  Color.ORANGE, Color.BLUE),
            (Color.WHITE,  Color.BLUE,   Color.RED),
            (Color.YELLOW, Color.ORANGE, Color.GREEN),
            (Color.YELLOW, Color.GREEN,  Color.RED),
            (Color.YELLOW, Color.BLUE,   Color.ORANGE),
            (Color.YELLOW, Color.RED,    Color.BLUE),
        ]
        edges = [
            (Color.WHITE,  Color.GREEN),
            (Color.WHITE,  Color.BLUE),
            (Color.WHITE,  Color.ORANGE),
            (Color.WHITE,  Color.RED),
            (Color.YELLOW, Color.GREEN),
            (Color.YELLOW, Color.BLUE),
            (Color.YELLOW, Color.ORANGE),
            (Color.YELLOW, Color.RED),
            (Color.GREEN,  Color.ORANGE),
            (Color.GREEN,  Color.RED),
            (Color.BLUE,   Color.ORANGE),
            (Color.BLUE,   Color.RED),
        ]
        # fmt: on
        with (
            patch("rubik_cube_solver.validator.validator.get_corners", return_value=corners),
            patch("rubik_cube_solver.validator.validator.get_edges", return_value=edges),
        ):
            validator._check_permutation_parity(cube)

    @pytest.mark.parametrize("cube_size", [3, 5])
    def test_exception_swap_two_corners(self, validator: Validator, cube_size: int) -> None:
        """
        Test that _check_permutation_parity raises ValueError when two corners are swapped (odd corner parity)
        while edges remain in solved order (even parity).

        :param validator: Fixture of a Validator instance
        :param cube_size: The size of the cube to validate
        :return: None
        """

        cube = Cube(cube_size)
        # Swap UFL and UFR corners — this creates one inversion (odd corner parity)
        # fmt: off
        corners = [
            (Color.WHITE,  Color.RED,    Color.GREEN),   # UFR in UFL slot
            (Color.WHITE,  Color.GREEN,  Color.ORANGE),  # UFL in UFR slot
            (Color.WHITE,  Color.ORANGE, Color.BLUE),
            (Color.WHITE,  Color.BLUE,   Color.RED),
            (Color.YELLOW, Color.ORANGE, Color.GREEN),
            (Color.YELLOW, Color.GREEN,  Color.RED),
            (Color.YELLOW, Color.BLUE,   Color.ORANGE),
            (Color.YELLOW, Color.RED,    Color.BLUE),
        ]
        edges = [
            (Color.WHITE,  Color.GREEN),
            (Color.WHITE,  Color.BLUE),
            (Color.WHITE,  Color.ORANGE),
            (Color.WHITE,  Color.RED),
            (Color.YELLOW, Color.GREEN),
            (Color.YELLOW, Color.BLUE),
            (Color.YELLOW, Color.ORANGE),
            (Color.YELLOW, Color.RED),
            (Color.GREEN,  Color.ORANGE),
            (Color.GREEN,  Color.RED),
            (Color.BLUE,   Color.ORANGE),
            (Color.BLUE,   Color.RED),
        ]
        # fmt: on
        with (
            patch("rubik_cube_solver.validator.validator.get_corners", return_value=corners),
            patch("rubik_cube_solver.validator.validator.get_edges", return_value=edges),
        ):
            with pytest.raises(ValueError, match="Invalid permutation parity"):
                validator._check_permutation_parity(cube)

    @pytest.mark.parametrize("cube_size", [3, 5])
    def test_exception_swap_two_edges(self, validator: Validator, cube_size: int) -> None:
        """
        Test that _check_permutation_parity raises ValueError when two edges are swapped (odd edge parity)
        while corners remain in solved order (even parity).

        :param validator: Fixture of a Validator instance
        :param cube_size: The size of the cube to validate
        :return: None
        """

        cube = Cube(cube_size)
        # fmt: off
        corners = [
            (Color.WHITE,  Color.GREEN,  Color.ORANGE),
            (Color.WHITE,  Color.RED,    Color.GREEN),
            (Color.WHITE,  Color.ORANGE, Color.BLUE),
            (Color.WHITE,  Color.BLUE,   Color.RED),
            (Color.YELLOW, Color.ORANGE, Color.GREEN),
            (Color.YELLOW, Color.GREEN,  Color.RED),
            (Color.YELLOW, Color.BLUE,   Color.ORANGE),
            (Color.YELLOW, Color.RED,    Color.BLUE),
        ]
        # Swap UF and UB corners — this creates one inversion (odd edge parity)
        edges = [
            (Color.WHITE,  Color.BLUE),   # UB in UF slot
            (Color.WHITE,  Color.GREEN),  # UF in UB slot
            (Color.WHITE,  Color.ORANGE),
            (Color.WHITE,  Color.RED),
            (Color.YELLOW, Color.GREEN),
            (Color.YELLOW, Color.BLUE),
            (Color.YELLOW, Color.ORANGE),
            (Color.YELLOW, Color.RED),
            (Color.GREEN,  Color.ORANGE),
            (Color.GREEN,  Color.RED),
            (Color.BLUE,   Color.ORANGE),
            (Color.BLUE,   Color.RED),
        ]
        # fmt: on
        with (
            patch("rubik_cube_solver.validator.validator.get_corners", return_value=corners),
            patch("rubik_cube_solver.validator.validator.get_edges", return_value=edges),
        ):
            with pytest.raises(ValueError, match="Invalid permutation parity"):
                validator._check_permutation_parity(cube)
