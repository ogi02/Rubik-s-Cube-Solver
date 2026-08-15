# Python imports
import pytest

# Project imports
from rubik_cube_solver.enums.CornerSlot import CornerSlot


class TestCornerSlotFromValue:
    # fmt: off
    @pytest.mark.parametrize(
        "value, expected", [
            ("UFL", CornerSlot.UFL),
            ("UFR", CornerSlot.UFR),
            ("UBL", CornerSlot.UBL),
            ("UBR", CornerSlot.UBR),
            ("DFL", CornerSlot.DFL),
            ("DFR", CornerSlot.DFR),
            ("DBL", CornerSlot.DBL),
            ("DBR", CornerSlot.DBR),
        ]
    )
    # fmt: on
    def test_success(self, value: str, expected: CornerSlot) -> None:
        """
        Tests creating a CornerSlot from string.

        :param value: The string value
        :param expected: The expected CornerSlot enumeration value
        :return: None
        """

        # Assert
        assert CornerSlot.from_value(value) == expected

    # fmt: off
    @pytest.mark.parametrize(
        "value", [
            "",
            "U",
            "FUL",
            "ufl",
        ]
    )
    # fmt: on
    def test_invalid_value(self, value: str) -> None:
        """
        Tests that creating a CornerSlot from an invalid string raises a ValueError.

        :param value: The string value
        :return: None
        """

        # Assert
        with pytest.raises(ValueError, match=f"Invalid value {value} for the CornerSlot enumeration"):
            CornerSlot.from_value(value)
