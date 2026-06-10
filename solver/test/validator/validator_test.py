# Python imports
from unittest.mock import patch

import pytest

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.validator.validator import Validator


class TestValidatorValidate:
    def test_success_3x3(self, validator: Validator) -> None:
        """
        Test that validate calls all 9 check methods exactly once for a 3x3 cube.

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
            patch.object(validator, "_check_edge_validity") as mock_check_edge_validity,
            patch.object(validator, "_check_edge_flip_parity") as mock_check_edge_flip_parity,
            patch.object(validator, "_check_permutation_parity") as mock_check_permutation_parity,
        ):
            validator.validate(cube)
            mock_check_size.assert_called_once_with(cube)
            mock_check_color_count.assert_called_once_with(cube)
            mock_check_corner_validity.assert_called_once_with(cube)
            mock_check_corner_orientation.assert_called_once_with(cube)
            mock_check_corner_chirality.assert_called_once_with(cube)
            mock_check_center_uniqueness.assert_called_once_with(cube)
            mock_check_edge_validity.assert_called_once_with(cube)
            mock_check_edge_flip_parity.assert_called_once_with(cube)
            mock_check_permutation_parity.assert_called_once_with(cube)

    # fmt: off
    @pytest.mark.parametrize(
        "cube_size", [2, 4, 5]
    )
    # fmt: on
    def test_success_non_3x3(self, validator: Validator, cube_size: int) -> None:
        """
        Test that validate does not call the 4 new 3x3-specific check methods for non-3x3 cubes.

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
            patch.object(validator, "_check_edge_validity") as mock_check_edge_validity,
            patch.object(validator, "_check_edge_flip_parity") as mock_check_edge_flip_parity,
            patch.object(validator, "_check_permutation_parity") as mock_check_permutation_parity,
        ):
            validator.validate(cube)
            mock_check_size.assert_called_once_with(cube)
            mock_check_color_count.assert_called_once_with(cube)
            mock_check_corner_validity.assert_called_once_with(cube)
            mock_check_corner_orientation.assert_called_once_with(cube)
            mock_check_corner_chirality.assert_called_once_with(cube)
            mock_check_center_uniqueness.assert_not_called()
            mock_check_edge_validity.assert_not_called()
            mock_check_edge_flip_parity.assert_not_called()
            mock_check_permutation_parity.assert_not_called()

    def test_check_center_uniqueness_exception(self, validator: Validator) -> None:
        """
        Test that validate propagates ValueError from _check_center_uniqueness and does not call subsequent checks.

        :param validator: Fixture of a Validator instance
        :return: None
        """

        cube = Cube(3)
        with (
            patch.object(validator, "_check_size"),
            patch.object(validator, "_check_color_count"),
            patch.object(validator, "_check_corner_validity"),
            patch.object(validator, "_check_corner_orientation"),
            patch.object(validator, "_check_corner_chirality"),
            patch.object(
                validator,
                "_check_center_uniqueness",
                side_effect=ValueError("Duplicate center piece."),
            ) as mock_check_center_uniqueness,
            patch.object(validator, "_check_edge_validity") as mock_check_edge_validity,
            patch.object(validator, "_check_edge_flip_parity") as mock_check_edge_flip_parity,
            patch.object(validator, "_check_permutation_parity") as mock_check_permutation_parity,
        ):
            with pytest.raises(ValueError, match="Duplicate center piece"):
                validator.validate(cube)
            mock_check_center_uniqueness.assert_called_once_with(cube)
            mock_check_edge_validity.assert_not_called()
            mock_check_edge_flip_parity.assert_not_called()
            mock_check_permutation_parity.assert_not_called()

    def test_check_edge_validity_exception(self, validator: Validator) -> None:
        """
        Test that validate propagates ValueError from _check_edge_validity and does not call subsequent checks.

        :param validator: Fixture of a Validator instance
        :return: None
        """

        cube = Cube(3)
        with (
            patch.object(validator, "_check_size"),
            patch.object(validator, "_check_color_count"),
            patch.object(validator, "_check_corner_validity"),
            patch.object(validator, "_check_corner_orientation"),
            patch.object(validator, "_check_corner_chirality"),
            patch.object(validator, "_check_center_uniqueness"),
            patch.object(
                validator,
                "_check_edge_validity",
                side_effect=ValueError("Invalid edge piece."),
            ) as mock_check_edge_validity,
            patch.object(validator, "_check_edge_flip_parity") as mock_check_edge_flip_parity,
            patch.object(validator, "_check_permutation_parity") as mock_check_permutation_parity,
        ):
            with pytest.raises(ValueError, match="Invalid edge piece"):
                validator.validate(cube)
            mock_check_edge_validity.assert_called_once_with(cube)
            mock_check_edge_flip_parity.assert_not_called()
            mock_check_permutation_parity.assert_not_called()

    def test_check_edge_flip_parity_exception(self, validator: Validator) -> None:
        """
        Test that validate propagates ValueError from _check_edge_flip_parity and does not call subsequent checks.

        :param validator: Fixture of a Validator instance
        :return: None
        """

        cube = Cube(3)
        with (
            patch.object(validator, "_check_size"),
            patch.object(validator, "_check_color_count"),
            patch.object(validator, "_check_corner_validity"),
            patch.object(validator, "_check_corner_orientation"),
            patch.object(validator, "_check_corner_chirality"),
            patch.object(validator, "_check_center_uniqueness"),
            patch.object(validator, "_check_edge_validity"),
            patch.object(
                validator,
                "_check_edge_flip_parity",
                side_effect=ValueError("Invalid edge flip parity."),
            ) as mock_check_edge_flip_parity,
            patch.object(validator, "_check_permutation_parity") as mock_check_permutation_parity,
        ):
            with pytest.raises(ValueError, match="Invalid edge flip parity"):
                validator.validate(cube)
            mock_check_edge_flip_parity.assert_called_once_with(cube)
            mock_check_permutation_parity.assert_not_called()

    def test_check_permutation_parity_exception(self, validator: Validator) -> None:
        """
        Test that validate propagates ValueError from _check_permutation_parity.

        :param validator: Fixture of a Validator instance
        :return: None
        """

        cube = Cube(3)
        with (
            patch.object(validator, "_check_size"),
            patch.object(validator, "_check_color_count"),
            patch.object(validator, "_check_corner_validity"),
            patch.object(validator, "_check_corner_orientation"),
            patch.object(validator, "_check_corner_chirality"),
            patch.object(validator, "_check_center_uniqueness"),
            patch.object(validator, "_check_edge_validity"),
            patch.object(validator, "_check_edge_flip_parity"),
            patch.object(
                validator,
                "_check_permutation_parity",
                side_effect=ValueError("Invalid permutation parity."),
            ) as mock_check_permutation_parity,
        ):
            with pytest.raises(ValueError, match="Invalid permutation parity"):
                validator.validate(cube)
            mock_check_permutation_parity.assert_called_once_with(cube)

    def test_check_size_exception(self, validator: Validator) -> None:
        """
        Test that validate propagates ValueError from _check_size and does not call _check_color_count.

        :param validator: Fixture of a Validator instance
        :return: None
        """

        cube = Cube(1)
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

    def test_check_color_count_exception(self, validator: Validator) -> None:
        """
        Test that validate propagates ValueError from _check_color_count and still calls _check_size.

        :param validator: Fixture of a Validator instance
        :return: None
        """

        cube = Cube(2)
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

    def test_check_corner_validity_exception(self, validator: Validator) -> None:
        """
        Test that validate propagates ValueError from _check_corner_validity.

        :param validator: Fixture of a Validator instance
        :return: None
        """

        cube = Cube(2)
        with (
            patch.object(validator, "_check_size"),
            patch.object(validator, "_check_color_count"),
            patch.object(
                validator,
                "_check_corner_validity",
                side_effect=ValueError("Invalid corner piece."),
            ) as mock_check_corner_validity,
            patch.object(validator, "_check_corner_orientation") as mock_check_corner_orientation,
            patch.object(validator, "_check_corner_chirality") as mock_check_corner_chirality,
        ):
            with pytest.raises(ValueError, match="Invalid corner piece"):
                validator.validate(cube)
            mock_check_corner_validity.assert_called_once_with(cube)
            mock_check_corner_orientation.assert_not_called()
            mock_check_corner_chirality.assert_not_called()

    def test_check_corner_orientation_exception(self, validator: Validator) -> None:
        """
        Test that validate propagates ValueError from _check_corner_orientation.

        :param validator: Fixture of a Validator instance
        :return: None
        """

        cube = Cube(2)
        with (
            patch.object(validator, "_check_size"),
            patch.object(validator, "_check_color_count"),
            patch.object(validator, "_check_corner_validity"),
            patch.object(
                validator,
                "_check_corner_orientation",
                side_effect=ValueError("Invalid corner orientation parity."),
            ) as mock_check_corner_orientation,
            patch.object(validator, "_check_corner_chirality") as mock_check_corner_chirality,
        ):
            with pytest.raises(ValueError, match="Invalid corner orientation parity"):
                validator.validate(cube)
            mock_check_corner_orientation.assert_called_once_with(cube)
            mock_check_corner_chirality.assert_not_called()

    def test_check_corner_chirality_exception(self, validator: Validator) -> None:
        """
        Test that validate propagates ValueError from _check_corner_chirality.

        :param validator: Fixture of a Validator instance
        :return: None
        """

        cube = Cube(2)
        with (
            patch.object(validator, "_check_size"),
            patch.object(validator, "_check_color_count"),
            patch.object(validator, "_check_corner_validity"),
            patch.object(validator, "_check_corner_orientation"),
            patch.object(
                validator,
                "_check_corner_chirality",
                side_effect=ValueError("Invalid corner chirality."),
            ) as mock_check_corner_chirality,
        ):
            with pytest.raises(ValueError, match="Invalid corner chirality"):
                validator.validate(cube)
            mock_check_corner_chirality.assert_called_once_with(cube)


class TestValidatorCheckSize:
    # fmt: off
    @pytest.mark.parametrize(
        "cube_size", [2, 3, 4, 5]
    )
    # fmt: on
    def test_success(self, validator: Validator, cube_size: int) -> None:
        """
        Test that _check_size does not raise for valid cube sizes.

        :param validator: Fixture of a Validator instance
        :param cube_size: The size of the cube to check
        :return: None
        """

        cube = Cube(cube_size)
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


class TestValidatorGetCorners:
    def test_success(self, validator: Validator) -> None:
        """
        Test that _get_corners returns the expected corners.

        :param validator: Fixture of a Validator instance
        :return: None
        """

        cube = Cube(3)
        corners = validator._get_corners(cube)

        assert len(corners) == 8
        for corner in corners:
            assert isinstance(corner, tuple)
            assert len(corner) == 3


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
            (Color.WHITE, Color.ORANGE, Color.BLUE),  # UBL  (canonical: WHITE, ORANGE, BLUE)
            (Color.WHITE, Color.BLUE, Color.RED),  # UBR
            (Color.YELLOW, Color.ORANGE, Color.GREEN),  # DFL
            (Color.YELLOW, Color.GREEN, Color.RED),  # DFR
            (Color.YELLOW, Color.BLUE, Color.ORANGE),  # DBL
            (Color.YELLOW, Color.RED, Color.BLUE),  # DBR
        ]
        with patch.object(Validator, "_get_corners", return_value=corners):
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
        with patch.object(Validator, "_get_corners", return_value=corners):
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
        with patch.object(Validator, "_get_corners", return_value=corners):
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
        with patch.object(Validator, "_get_corners", return_value=corners):
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
        with patch.object(Validator, "_get_corners", return_value=corners):
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
        with patch.object(Validator, "_get_corners", return_value=corners):
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
        with patch.object(Validator, "_get_corners", return_value=corners):
            with pytest.raises(ValueError, match="Invalid corner chirality"):
                validator._check_corner_chirality(cube)


class TestValidatorGetEdges:
    def test_success(self, validator: Validator) -> None:
        """
        Test that _get_edges returns 12 edge tuples with correct sticker colors for a solved 3x3 cube.

        :param validator: Fixture of a Validator instance
        :return: None
        """

        cube = Cube(3)
        edges = validator._get_edges(cube)

        assert len(edges) == 12
        for edge in edges:
            assert isinstance(edge, tuple)
            assert len(edge) == 2
            assert isinstance(edge[0], Color)
            assert isinstance(edge[1], Color)

        # UF edge should be (WHITE, GREEN) for a solved cube
        assert edges[0] == (Color.WHITE, Color.GREEN)


class TestValidatorCheckCenterUniqueness:
    def test_success(self, validator: Validator) -> None:
        """
        Test that _check_center_uniqueness does not raise for a solved 3x3 cube.

        :param validator: Fixture of a Validator instance
        :return: None
        """

        cube = Cube(3)
        validator._check_center_uniqueness(cube)

    def test_exception_duplicate_center(self, validator: Validator) -> None:
        """
        Test that _check_center_uniqueness raises ValueError when two faces share the same center color.

        :param validator: Fixture of a Validator instance
        :return: None
        """

        # fmt: off
        cube = Cube(
            size=3,
            layers={
                Layer.UP:    [Color.WHITE,  Color.WHITE,  Color.WHITE,
                              Color.WHITE,  Color.WHITE,  Color.WHITE,
                              Color.WHITE,  Color.WHITE,  Color.WHITE],
                Layer.DOWN:  [Color.WHITE,  Color.WHITE,  Color.WHITE,
                              Color.WHITE,  Color.WHITE,  Color.WHITE,
                              Color.WHITE,  Color.WHITE,  Color.WHITE],
                Layer.LEFT:  [Color.ORANGE, Color.ORANGE, Color.ORANGE,
                              Color.ORANGE, Color.ORANGE, Color.ORANGE,
                              Color.ORANGE, Color.ORANGE, Color.ORANGE],
                Layer.RIGHT: [Color.RED,    Color.RED,    Color.RED,
                              Color.RED,    Color.RED,    Color.RED,
                              Color.RED,    Color.RED,    Color.RED],
                Layer.FRONT: [Color.GREEN,  Color.GREEN,  Color.GREEN,
                              Color.GREEN,  Color.GREEN,  Color.GREEN,
                              Color.GREEN,  Color.GREEN,  Color.GREEN],
                Layer.BACK:  [Color.BLUE,   Color.BLUE,   Color.BLUE,
                              Color.BLUE,   Color.BLUE,   Color.BLUE,
                              Color.BLUE,   Color.BLUE,   Color.BLUE],
            }
        )
        # fmt: on
        with pytest.raises(ValueError, match="Duplicate center piece"):
            validator._check_center_uniqueness(cube)


class TestValidatorCheckEdgeValidity:
    def test_success(self, validator: Validator) -> None:
        """
        Test that _check_edge_validity does not raise when all 12 edges are valid and distinct.

        :param validator: Fixture of a Validator instance
        :return: None
        """

        cube = Cube(3)
        edges = [
            (Color.WHITE, Color.GREEN),
            (Color.WHITE, Color.BLUE),
            (Color.WHITE, Color.ORANGE),
            (Color.WHITE, Color.RED),
            (Color.YELLOW, Color.GREEN),
            (Color.YELLOW, Color.BLUE),
            (Color.YELLOW, Color.ORANGE),
            (Color.YELLOW, Color.RED),
            (Color.GREEN, Color.ORANGE),
            (Color.GREEN, Color.RED),
            (Color.BLUE, Color.ORANGE),
            (Color.BLUE, Color.RED),
        ]
        with patch.object(Validator, "_get_edges", return_value=edges):
            validator._check_edge_validity(cube)

    def test_exception_invalid_edge(self, validator: Validator) -> None:
        """
        Test that _check_edge_validity raises ValueError when one edge has an impossible color combination.

        :param validator: Fixture of a Validator instance
        :return: None
        """

        cube = Cube(3)
        edges = [
            (Color.WHITE, Color.YELLOW),  # invalid: opposite faces cannot share an edge
            (Color.WHITE, Color.BLUE),
            (Color.WHITE, Color.ORANGE),
            (Color.WHITE, Color.RED),
            (Color.YELLOW, Color.GREEN),
            (Color.YELLOW, Color.BLUE),
            (Color.YELLOW, Color.ORANGE),
            (Color.YELLOW, Color.RED),
            (Color.GREEN, Color.ORANGE),
            (Color.GREEN, Color.RED),
            (Color.BLUE, Color.ORANGE),
            (Color.BLUE, Color.RED),
        ]
        with patch.object(Validator, "_get_edges", return_value=edges):
            with pytest.raises(ValueError, match="Invalid edge piece"):
                validator._check_edge_validity(cube)

    def test_exception_duplicate_edge(self, validator: Validator) -> None:
        """
        Test that _check_edge_validity raises ValueError when two edges have the same color set.

        :param validator: Fixture of a Validator instance
        :return: None
        """

        cube = Cube(3)
        edges = [
            (Color.WHITE, Color.GREEN),
            (Color.WHITE, Color.GREEN),  # duplicate of first edge
            (Color.WHITE, Color.ORANGE),
            (Color.WHITE, Color.RED),
            (Color.YELLOW, Color.GREEN),
            (Color.YELLOW, Color.BLUE),
            (Color.YELLOW, Color.ORANGE),
            (Color.YELLOW, Color.RED),
            (Color.GREEN, Color.ORANGE),
            (Color.GREEN, Color.RED),
            (Color.BLUE, Color.ORANGE),
            (Color.BLUE, Color.RED),
        ]
        with patch.object(Validator, "_get_edges", return_value=edges):
            with pytest.raises(ValueError, match="Duplicate edge piece"):
                validator._check_edge_validity(cube)


class TestValidatorCheckEdgeFlipParity:
    def test_success(self, validator: Validator) -> None:
        """
        Test that _check_edge_flip_parity does not raise when all 12 edges are in oriented position (total = 0).

        :param validator: Fixture of a Validator instance
        :return: None
        """

        cube = Cube(3)
        # All edges have the primary color in position 0 (orientation = 0, total = 0)
        edges = [
            (Color.WHITE, Color.GREEN),
            (Color.WHITE, Color.BLUE),
            (Color.WHITE, Color.ORANGE),
            (Color.WHITE, Color.RED),
            (Color.YELLOW, Color.GREEN),
            (Color.YELLOW, Color.BLUE),
            (Color.YELLOW, Color.ORANGE),
            (Color.YELLOW, Color.RED),
            (Color.GREEN, Color.ORANGE),
            (Color.GREEN, Color.RED),
            (Color.BLUE, Color.ORANGE),
            (Color.BLUE, Color.RED),
        ]
        with patch.object(Validator, "_get_edges", return_value=edges):
            validator._check_edge_flip_parity(cube)

    def test_exception(self, validator: Validator) -> None:
        """
        Test that _check_edge_flip_parity raises ValueError when one edge is flipped (total = 1, which is odd).

        :param validator: Fixture of a Validator instance
        :return: None
        """

        cube = Cube(3)
        # UF edge is flipped: GREEN is in position 0 instead of WHITE (orientation = 1, total = 1)
        edges = [
            (Color.GREEN, Color.WHITE),  # flipped UF edge
            (Color.WHITE, Color.BLUE),
            (Color.WHITE, Color.ORANGE),
            (Color.WHITE, Color.RED),
            (Color.YELLOW, Color.GREEN),
            (Color.YELLOW, Color.BLUE),
            (Color.YELLOW, Color.ORANGE),
            (Color.YELLOW, Color.RED),
            (Color.GREEN, Color.ORANGE),
            (Color.GREEN, Color.RED),
            (Color.BLUE, Color.ORANGE),
            (Color.BLUE, Color.RED),
        ]
        with patch.object(Validator, "_get_edges", return_value=edges):
            with pytest.raises(ValueError, match="Invalid edge flip parity"):
                validator._check_edge_flip_parity(cube)


class TestValidatorCheckPermutationParity:
    def test_success(self, validator: Validator) -> None:
        """
        Test that _check_permutation_parity does not raise when corners and edges are both in solved order (both even).

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
        edges = [
            (Color.WHITE, Color.GREEN),
            (Color.WHITE, Color.BLUE),
            (Color.WHITE, Color.ORANGE),
            (Color.WHITE, Color.RED),
            (Color.YELLOW, Color.GREEN),
            (Color.YELLOW, Color.BLUE),
            (Color.YELLOW, Color.ORANGE),
            (Color.YELLOW, Color.RED),
            (Color.GREEN, Color.ORANGE),
            (Color.GREEN, Color.RED),
            (Color.BLUE, Color.ORANGE),
            (Color.BLUE, Color.RED),
        ]
        with (
            patch.object(Validator, "_get_corners", return_value=corners),
            patch.object(Validator, "_get_edges", return_value=edges),
        ):
            validator._check_permutation_parity(cube)

    def test_exception(self, validator: Validator) -> None:
        """
        Test that _check_permutation_parity raises ValueError when two corners are swapped (odd corner parity)
        while edges remain in solved order (even parity).

        :param validator: Fixture of a Validator instance
        :return: None
        """

        cube = Cube(3)
        # Swap UFL and UFR corners — this creates one inversion (odd corner parity)
        corners = [
            (Color.WHITE, Color.RED, Color.GREEN),  # UFR in UFL slot
            (Color.WHITE, Color.GREEN, Color.ORANGE),  # UFL in UFR slot
            (Color.WHITE, Color.ORANGE, Color.BLUE),  # UBL
            (Color.WHITE, Color.BLUE, Color.RED),  # UBR
            (Color.YELLOW, Color.ORANGE, Color.GREEN),  # DFL
            (Color.YELLOW, Color.GREEN, Color.RED),  # DFR
            (Color.YELLOW, Color.BLUE, Color.ORANGE),  # DBL
            (Color.YELLOW, Color.RED, Color.BLUE),  # DBR
        ]
        edges = [
            (Color.WHITE, Color.GREEN),
            (Color.WHITE, Color.BLUE),
            (Color.WHITE, Color.ORANGE),
            (Color.WHITE, Color.RED),
            (Color.YELLOW, Color.GREEN),
            (Color.YELLOW, Color.BLUE),
            (Color.YELLOW, Color.ORANGE),
            (Color.YELLOW, Color.RED),
            (Color.GREEN, Color.ORANGE),
            (Color.GREEN, Color.RED),
            (Color.BLUE, Color.ORANGE),
            (Color.BLUE, Color.RED),
        ]
        with (
            patch.object(Validator, "_get_corners", return_value=corners),
            patch.object(Validator, "_get_edges", return_value=edges),
        ):
            with pytest.raises(ValueError, match="Invalid permutation parity"):
                validator._check_permutation_parity(cube)
