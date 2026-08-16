# Python imports
import pytest

# Project imports
from rubik_cube_solver.enums.Rotation import Rotation


class TestRotationFromValue:
    # fmt: off
    @pytest.mark.parametrize(
        "value, expected", [
            ("x", Rotation.X),
            ("y", Rotation.Y),
            ("z", Rotation.Z),
        ]
    )
    # fmt: on
    def test_success(self, value: str, expected: Rotation) -> None:
        """
        Tests creating a Rotation from string.

        :param value: The string value
        :param expected: The expected Rotation enumeration value
        :return: None
        """

        # Assert
        assert Rotation.from_value(value) == expected

    # fmt: off
    @pytest.mark.parametrize(
        "value", [
            "",
            "X",
            "w",
        ]
    )
    # fmt: on
    def test_invalid_value(self, value: str) -> None:
        """
        Tests that creating a Rotation from an invalid string raises a ValueError.

        :param value: The string value
        :return: None
        """

        # Assert
        with pytest.raises(ValueError, match=f"Invalid value {value} for the Rotation enumeration"):
            Rotation.from_value(value)
