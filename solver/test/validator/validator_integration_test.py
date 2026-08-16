# Python imports
import pytest

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.cube_rotation.rotator import Rotator
from rubik_cube_solver.scramble.scrambler import Scrambler
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
            "scrambled_3x3_cube",
            "scrambled_4x4_cube",
            "scrambled_5x5_cube",
            "scrambled_6x6_cube",
            "scrambled_7x7_cube",
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
        "rotation", [
            "x", "x'", "x2",
            "y", "y'", "y2",
            "z", "z'", "z2",
        ]
    )
    # fmt: on
    def test_success_reoriented_3x3(self, validator: Validator, rotation: str) -> None:
        """
        Test that a solved 3x3 cube reoriented by any whole-cube rotation passes validation.

        :param validator: Fixture of a Validator instance
        :param rotation: The whole-cube rotation applied to the solved cube
        :return: None
        """

        cube = Cube(3)
        Rotator(cube).apply(Algorithm.from_str(rotation))
        validator.validate(cube)

    def test_success_scrambled_reoriented_3x3(self, validator: Validator) -> None:
        """
        Test that a scrambled 3x3 cube reoriented by a quarter whole-cube rotation passes validation.

        :param validator: Fixture of a Validator instance
        :return: None
        """

        cube = Cube(3)
        rotator = Rotator(cube)
        for move in Scrambler().generate_scramble(3):
            rotator.turn(move)
        rotator.apply(Algorithm.from_str("x"))

        validator.validate(cube)
