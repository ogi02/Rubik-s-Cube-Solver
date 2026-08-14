# Python imports
import pytest

# Project imports
from rubik_cube_solver.enums.EdgeSlot import EdgeSlot


class TestEdgeSlotFromValue:
    # fmt: off
    @pytest.mark.parametrize(
        "value, expected", [
            ("UF", EdgeSlot.UF),
            ("UB", EdgeSlot.UB),
            ("UL", EdgeSlot.UL),
            ("UR", EdgeSlot.UR),
            ("DF", EdgeSlot.DF),
            ("DB", EdgeSlot.DB),
            ("DL", EdgeSlot.DL),
            ("DR", EdgeSlot.DR),
            ("FL", EdgeSlot.FL),
            ("FR", EdgeSlot.FR),
            ("BL", EdgeSlot.BL),
            ("BR", EdgeSlot.BR),
        ]
    )
    # fmt: on
    def test_success(self, value: str, expected: EdgeSlot) -> None:
        """
        Tests creating an EdgeSlot from string.

        :param value: The string value
        :param expected: The expected EdgeSlot enumeration value
        :return: None
        """

        # Assert
        assert EdgeSlot.from_value(value) == expected

    # fmt: off
    @pytest.mark.parametrize(
        "value", [
            "",
            "U",
            "FU",
            "uf",
        ]
    )
    # fmt: on
    def test_invalid_value(self, value: str) -> None:
        """
        Tests that creating an EdgeSlot from an invalid string raises a ValueError.

        :param value: The string value
        :return: None
        """

        # Assert
        with pytest.raises(ValueError, match=f"Invalid value {value} for the EdgeSlot enumeration"):
            EdgeSlot.from_value(value)
