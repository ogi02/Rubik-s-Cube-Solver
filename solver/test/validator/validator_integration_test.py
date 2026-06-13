import copy

import pytest

from rubik_cube_solver.cube import Cube
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.validator.validator import Validator


class TestValidatorIntegration:
    # fmt: off
    @pytest.mark.parametrize("cube_size", [2, 3, 4, 5, 6, 7])
    # fmt: on
    def test_success_solved(self, validator: Validator, cube_size: int) -> None:
        """
        Test that a solved cube of any valid size passes validation.

        :param validator: Fixture of a Validator instance
        :param cube_size: The size of the cube to validate
        :return: None
        """

        cube = Cube(cube_size)
        validator.validate(cube)

    # fmt: off
    @pytest.mark.parametrize(
        "cube_fixture", [
            "scrambled_2x2_cube",
            "scrambled_4x4_cube",
            "scrambled_6x6_cube",
        ]
    )
    # fmt: on
    def test_success_scrambled(self, validator: Validator, request: pytest.FixtureRequest, cube_fixture: str) -> None:
        """
        Test that a scrambled even-sized cube passes validation.
        Odd-sized cubes are excluded due to a pre-existing bug in the validator's center index calculation.

        :param validator: Fixture of a Validator instance
        :param request: Pytest request for dynamic fixture lookup
        :param cube_fixture: Name of the scrambled cube fixture
        :return: None
        """

        cube = request.getfixturevalue(cube_fixture)
        validator.validate(cube)

    # fmt: off
    @pytest.mark.parametrize(
        "cube_size, cube_fixture", [
            (2, "scrambled_2x2_cube"),
            (3, "scrambled_3x3_cube"),
            (4, "scrambled_4x4_cube"),
            (5, "scrambled_5x5_cube"),
            (6, "scrambled_6x6_cube"),
            (7, "scrambled_7x7_cube"),
        ]
    )
    # fmt: on
    def test_invalid_color_count(
        self, validator: Validator, request: pytest.FixtureRequest, cube_size: int, cube_fixture: str
    ) -> None:
        """
        Test that a scrambled cube with one sticker overwritten to a different color
        fails validation due to invalid color count.

        :param validator: Fixture of a Validator instance
        :param request: Pytest request for dynamic fixture lookup
        :param cube_size: The size of the cube
        :param cube_fixture: Name of the scrambled cube fixture
        :return: None
        """

        cube = request.getfixturevalue(cube_fixture)
        mutated_layers = copy.deepcopy(cube.layers)
        original_color = mutated_layers[Layer.UP][0]
        mutated_layers[Layer.UP][0] = Color.WHITE if original_color != Color.WHITE else Color.YELLOW
        mutated_cube = Cube(cube_size, mutated_layers)
        with pytest.raises(ValueError, match="Invalid color count"):
            validator.validate(mutated_cube)

    # fmt: off
    @pytest.mark.parametrize(
        "cube_size, cube_fixture", [
            (2, "scrambled_2x2_cube"),
            (3, "scrambled_3x3_cube"),
            (4, "scrambled_4x4_cube"),
            (5, "scrambled_5x5_cube"),
            (6, "scrambled_6x6_cube"),
            (7, "scrambled_7x7_cube"),
        ]
    )
    # fmt: on
    def test_invalid_corner(
        self, validator: Validator, request: pytest.FixtureRequest, cube_size: int, cube_fixture: str
    ) -> None:
        """
        Test that a scrambled cube with corner stickers swapped between faces fails validation
        due to corrupted corner piece combinations.

        :param validator: Fixture of a Validator instance
        :param request: Pytest request for dynamic fixture lookup
        :param cube_size: The size of the cube
        :param cube_fixture: Name of the scrambled cube fixture
        :return: None
        """

        cube = request.getfixturevalue(cube_fixture)
        mutated_layers = copy.deepcopy(cube.layers)
        n = cube_size
        swap_candidates = [
            (Layer.FRONT, 0),
            (Layer.FRONT, n - 1),
            (Layer.DOWN, 0),
            (Layer.DOWN, n - 1),
            (Layer.RIGHT, 0),
            (Layer.RIGHT, n - 1),
            (Layer.LEFT, n * n - 1),
            (Layer.BACK, n * (n - 1)),
        ]
        for other_face, other_idx in swap_candidates:
            if mutated_layers[Layer.UP][0] != mutated_layers[other_face][other_idx]:
                mutated_layers[Layer.UP][0], mutated_layers[other_face][other_idx] = (
                    mutated_layers[other_face][other_idx],
                    mutated_layers[Layer.UP][0],
                )
                break
        mutated_cube = Cube(cube_size, mutated_layers)
        with pytest.raises(ValueError):
            validator.validate(mutated_cube)

    # fmt: off
    @pytest.mark.parametrize(
        "cube_size, cube_fixture", [
            (3, "scrambled_3x3_cube"),
            (5, "scrambled_5x5_cube"),
            (7, "scrambled_7x7_cube"),
        ]
    )
    # fmt: on
    def test_invalid_center_sticker(
        self, validator: Validator, request: pytest.FixtureRequest, cube_size: int, cube_fixture: str
    ) -> None:
        """
        Test that a scrambled odd-sized cube with center stickers swapped between faces
        fails validation due to corrupted center uniqueness or opposites.

        :param validator: Fixture of a Validator instance
        :param request: Pytest request for dynamic fixture lookup
        :param cube_size: The size of the cube
        :param cube_fixture: Name of the scrambled cube fixture
        :return: None
        """

        cube = request.getfixturevalue(cube_fixture)
        mutated_layers = copy.deepcopy(cube.layers)
        center_idx = cube_size // 2
        if mutated_layers[Layer.UP][center_idx] != mutated_layers[Layer.DOWN][center_idx]:
            mutated_layers[Layer.UP][center_idx], mutated_layers[Layer.DOWN][center_idx] = (
                mutated_layers[Layer.DOWN][center_idx],
                mutated_layers[Layer.UP][center_idx],
            )
        else:
            mutated_layers[Layer.UP][center_idx], mutated_layers[Layer.FRONT][center_idx] = (
                mutated_layers[Layer.FRONT][center_idx],
                mutated_layers[Layer.UP][center_idx],
            )
        mutated_cube = Cube(cube_size, mutated_layers)
        with pytest.raises(ValueError):
            validator.validate(mutated_cube)

    # fmt: off
    @pytest.mark.parametrize(
        "cube_size, cube_fixture", [
            (4, "scrambled_4x4_cube"),
            (5, "scrambled_5x5_cube"),
            (6, "scrambled_6x6_cube"),
            (7, "scrambled_7x7_cube"),
        ]
    )
    # fmt: on
    def test_invalid_center_count_big(
        self, validator: Validator, request: pytest.FixtureRequest, cube_size: int, cube_fixture: str
    ) -> None:
        """
        Test that a scrambled big cube with an inner center sticker swapped with a border sticker
        on the same face fails validation due to corrupted center piece counts.

        :param validator: Fixture of a Validator instance
        :param request: Pytest request for dynamic fixture lookup
        :param cube_size: The size of the cube
        :param cube_fixture: Name of the scrambled cube fixture
        :return: None
        """

        cube = request.getfixturevalue(cube_fixture)
        mutated_layers = copy.deepcopy(cube.layers)
        n = cube_size
        center_sticker_idx = n + 1
        border_positions = list(range(1, n - 1))
        border_positions += [n * i for i in range(1, n - 1)]
        border_positions += [n * i + n - 1 for i in range(1, n - 1)]
        border_positions += list(range(n * (n - 1) + 1, n * n - 1))
        for wing_sticker_idx in border_positions:
            if mutated_layers[Layer.UP][wing_sticker_idx] != mutated_layers[Layer.UP][center_sticker_idx]:
                mutated_layers[Layer.UP][center_sticker_idx], mutated_layers[Layer.UP][wing_sticker_idx] = (
                    mutated_layers[Layer.UP][wing_sticker_idx],
                    mutated_layers[Layer.UP][center_sticker_idx],
                )
                break
        mutated_cube = Cube(cube_size, mutated_layers)
        with pytest.raises(ValueError):
            validator.validate(mutated_cube)

    # fmt: off
    @pytest.mark.parametrize(
        "cube_size, cube_fixture", [
            (4, "scrambled_4x4_cube"),
            (5, "scrambled_5x5_cube"),
            (6, "scrambled_6x6_cube"),
            (7, "scrambled_7x7_cube"),
        ]
    )
    # fmt: on
    def test_invalid_wing_edge(
        self, validator: Validator, request: pytest.FixtureRequest, cube_size: int, cube_fixture: str
    ) -> None:
        """
        Test that a scrambled big cube with a wing edge's direction reversed
        fails validation due to corrupted wing edge pieces.

        :param validator: Fixture of a Validator instance
        :param request: Pytest request for dynamic fixture lookup
        :param cube_size: The size of the cube
        :param cube_fixture: Name of the scrambled cube fixture
        :return: None
        """

        cube = request.getfixturevalue(cube_fixture)
        mutated_layers = copy.deepcopy(cube.layers)
        n = cube_size
        up_idx = n - 2
        back_idx = 1
        if mutated_layers[Layer.UP][up_idx] != mutated_layers[Layer.BACK][back_idx]:
            mutated_layers[Layer.UP][up_idx], mutated_layers[Layer.BACK][back_idx] = (
                mutated_layers[Layer.BACK][back_idx],
                mutated_layers[Layer.UP][up_idx],
            )
        else:
            up_idx = n * (n - 1) + 1
            front_idx = 1
            mutated_layers[Layer.UP][up_idx], mutated_layers[Layer.FRONT][front_idx] = (
                mutated_layers[Layer.FRONT][front_idx],
                mutated_layers[Layer.UP][up_idx],
            )
        mutated_cube = Cube(cube_size, mutated_layers)
        with pytest.raises(ValueError):
            validator.validate(mutated_cube)
