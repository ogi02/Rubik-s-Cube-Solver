# Python imports
import pytest

# Project imports
from rubik_cube_solver.enums.Direction import Direction


class TestDirectionFromValue:
    # fmt: off
    @pytest.mark.parametrize(
        "value, expected", [
            ("",  Direction.CW),
            ("'", Direction.CCW),
            ("2", Direction.DOUBLE),
        ]
    )
    # fmt: on
    def test_success(self, value: str, expected: Direction) -> None:
        """
        Tests creating a Direction from string.

        :param value: The string value
        :param expected: The expected Direction enumeration value
        :return: None
        """

        # Assert
        assert Direction.from_value(value) == expected

    # fmt: off
    @pytest.mark.parametrize(
        "value", [
            "3",
            "x",
        ]
    )
    # fmt: on
    def test_invalid_value(self, value: str) -> None:
        """
        Tests that creating a Direction from an invalid string raises a ValueError.

        :param value: The string value
        :return: None
        """

        # Assert
        with pytest.raises(ValueError, match=f"Invalid value {value} for the Direction enumeration"):
            Direction.from_value(value)


class TestDirectionInverse:
    # fmt: off
    @pytest.mark.parametrize(
        "direction, expected", [
            (Direction.CW,     Direction.CCW),
            (Direction.CCW,    Direction.CW),
            (Direction.DOUBLE, Direction.DOUBLE),
        ]
    )
    # fmt: on
    def test_success(self, direction: Direction, expected: Direction) -> None:
        """
        Tests that a quarter turn is undone by the quarter turn the other way, and a double turn by
        itself.

        :param direction: The direction to invert
        :param expected: The direction that undoes it
        :return: None
        """

        # Assert
        assert direction.inverse() is expected
