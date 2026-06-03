# Python imports
from typing import Callable
from unittest.mock import patch

import pytest

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.validator.validator import Validator


class TestValidatorValidate:
    # fmt: off
    @pytest.mark.parametrize(
        "cube_size", [2, 3, 4, 5]
    )
    # fmt: on
    def test_success(
        self,
        validator: Validator,
        generate_cube: Callable[[int], Cube],
        cube_size: int,
    ) -> None:
        """
        Test that validate calls both private check methods exactly once.

        :param validator: Fixture of a Validator instance
        :param generate_cube: Fixture that creates a Cube of given size
        :param cube_size: The size of the cube to validate
        :return: None
        """

        cube = generate_cube(cube_size)
        with (
            patch.object(validator, "_check_size") as mock_check_size,
            patch.object(validator, "_check_color_count") as mock_check_color_count,
        ):
            result = validator.validate(cube)
            assert result is None
            mock_check_size.assert_called_once_with(cube)
            mock_check_color_count.assert_called_once_with(cube)

    def test_check_size_exception(self, validator: Validator, generate_cube: Callable[[int], Cube]) -> None:
        """
        Test that validate propagates ValueError from _check_size and does not call _check_color_count.

        :param validator: Fixture of a Validator instance
        :param generate_cube: Fixture that creates a Cube of given size
        :return: None
        """

        cube = generate_cube(2)
        with (
            patch.object(
                validator, "_check_size", side_effect=ValueError("Cube size must be at least 2.")
            ) as mock_check_size,
            patch.object(validator, "_check_color_count") as mock_check_color_count,
        ):
            with pytest.raises(ValueError, match="Cube size must be at least 2."):
                validator.validate(cube)
            mock_check_size.assert_called_once_with(cube)
            mock_check_color_count.assert_not_called()

    def test_check_color_count_exception(self, validator: Validator, generate_cube: Callable[[int], Cube]) -> None:
        """
        Test that validate propagates ValueError from _check_color_count and still calls _check_size.

        :param validator: Fixture of a Validator instance
        :param generate_cube: Fixture that creates a Cube of given size
        :return: None
        """

        cube = generate_cube(2)
        with (
            patch.object(validator, "_check_size") as mock_check_size,
            patch.object(
                validator,
                "_check_color_count",
                side_effect=ValueError("Invalid color count for WHITE: expected 4, got 3."),
            ) as mock_check_color_count,
        ):
            with pytest.raises(ValueError, match=r"Invalid color count for WHITE: expected 4, got 3\."):
                validator.validate(cube)
            mock_check_size.assert_called_once_with(cube)
            mock_check_color_count.assert_called_once_with(cube)


class TestValidatorCheckSize:
    # fmt: off
    @pytest.mark.parametrize(
        "cube_size", [2, 3, 4, 5]
    )
    # fmt: on
    def test_success(self, validator: Validator, generate_cube: Callable[[int], Cube], cube_size: int) -> None:
        """
        Test that _check_size does not raise for valid cube sizes.

        :param validator: Fixture of a Validator instance
        :param generate_cube: Fixture that creates a Cube of given size
        :param cube_size: The size of the cube to check
        :return: None
        """

        cube = generate_cube(cube_size)
        validator._check_size(cube)

    # fmt: off
    @pytest.mark.parametrize(
        "cube_size", [1, 0, -1]
    )
    # fmt: on
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
    # fmt: off
    @pytest.mark.parametrize(
        "cube_size", [2, 3, 4, 5]
    )
    # fmt: on
    def test_success(self, validator: Validator, generate_cube: Callable[[int], Cube], cube_size: int) -> None:
        """
        Test that _check_color_count does not raise for a solved cube of any valid size.

        :param validator: Fixture of a Validator instance
        :param generate_cube: Fixture that creates a Cube of given size
        :param cube_size: The size of the cube to check
        :return: None
        """

        cube = generate_cube(cube_size)
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
