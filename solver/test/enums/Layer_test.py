# Python imports
import re

import pytest

# Project imports
from rubik_cube_solver.enums.Layer import Layer


class TestLayerFromValue:
    # fmt: off
    @pytest.mark.parametrize(
        "value, expected", [
            ("U", Layer.UP),
            ("D", Layer.DOWN),
            ("L", Layer.LEFT),
            ("R", Layer.RIGHT),
            ("F", Layer.FRONT),
            ("B", Layer.BACK),
        ]
    )
    # fmt: on
    def test_success(self, value: str, expected: Layer) -> None:
        """
        Tests creating a Layer from string.

        :param value: The string value
        :param expected: The expected Layer enumeration value
        :return: None
        """

        # Assert
        assert Layer.from_value(value) == expected

    # fmt: off
    @pytest.mark.parametrize(
        "value", [
            "",
            "X",
            "u",
        ]
    )
    # fmt: on
    def test_invalid_value(self, value: str) -> None:
        """
        Tests that creating a Layer from an invalid string raises a ValueError.

        :param value: The string value
        :return: None
        """

        # Assert
        with pytest.raises(ValueError, match=re.escape(f"Invalid value {value} for the Layer enumeration")):
            Layer.from_value(value)
