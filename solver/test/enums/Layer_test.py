# Python imports
import pytest

# Project imports
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.enums.Rotation import Rotation


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
        with pytest.raises(ValueError, match=f"Invalid value {value} for the Layer enumeration"):
            Layer.from_value(value)


class TestLayerOpposite:
    # fmt: off
    @pytest.mark.parametrize(
        "layer, expected", [
            (Layer.UP,    Layer.DOWN),
            (Layer.DOWN,  Layer.UP),
            (Layer.LEFT,  Layer.RIGHT),
            (Layer.RIGHT, Layer.LEFT),
            (Layer.FRONT, Layer.BACK),
            (Layer.BACK,  Layer.FRONT),
        ]
    )
    # fmt: on
    def test_success(self, layer: Layer, expected: Layer) -> None:
        """
        Tests that every face is paired with the face on the other side of the cube.

        :param layer: The face
        :param expected: The opposite face
        :return: None
        """

        # Assert
        assert layer.opposite() is expected


class TestLayerAxis:
    # fmt: off
    @pytest.mark.parametrize(
        "layer, expected", [
            (Layer.UP,    Rotation.Y),
            (Layer.DOWN,  Rotation.Y),
            (Layer.LEFT,  Rotation.X),
            (Layer.RIGHT, Rotation.X),
            (Layer.FRONT, Rotation.Z),
            (Layer.BACK,  Rotation.Z),
        ]
    )
    # fmt: on
    def test_success(self, layer: Layer, expected: Rotation) -> None:
        """
        Tests that every face is paired with the rotation about its own axis.

        :param layer: The face
        :param expected: The rotation axis
        :return: None
        """

        # Assert
        assert layer.axis() is expected


class TestLayerFromAxis:
    # fmt: off
    @pytest.mark.parametrize(
        "axis, expected", [
            (Rotation.X, Layer.RIGHT),
            (Rotation.Y, Layer.UP),
            (Rotation.Z, Layer.FRONT),
        ]
    )
    # fmt: on
    def test_success(self, axis: Rotation, expected: Layer) -> None:
        """
        Tests that each rotation axis is paired with the face it turns like.

        :param axis: The rotation axis
        :param expected: The expected face
        :return: None
        """

        # Assert
        assert Layer.from_axis(axis) is expected

    # fmt: off
    @pytest.mark.parametrize(
        "layer", [
            Layer.RIGHT,
            Layer.UP,
            Layer.FRONT,
        ]
    )
    # fmt: on
    def test_round_trips_with_axis(self, layer: Layer) -> None:
        """
        Tests that from_axis is the inverse of axis for the three faces that turn with their axis.

        :param layer: The face
        :return: None
        """

        # Assert
        assert Layer.from_axis(layer.axis()) is layer


class TestLayerTurnsWithAxis:
    # fmt: off
    @pytest.mark.parametrize(
        "layer, expected", [
            (Layer.UP,    True),
            (Layer.DOWN,  False),
            (Layer.LEFT,  False),
            (Layer.RIGHT, True),
            (Layer.FRONT, True),
            (Layer.BACK,  False),
        ]
    )
    # fmt: on
    def test_success(self, layer: Layer, expected: bool) -> None:
        """
        Tests that RIGHT, UP and FRONT turn with their axis's rotation, and their opposite faces
        against it.

        :param layer: The face
        :param expected: Whether a clockwise turn of the face turns like the rotation
        :return: None
        """

        # Assert
        assert layer.turns_with_axis() is expected
