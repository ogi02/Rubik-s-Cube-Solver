# Python imports
import pytest

# Project imports
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.cube_rotation.move import Move
from rubik_cube_solver.cube_rotation.orientation import Orientation
from rubik_cube_solver.enums.Direction import Direction
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.enums.Rotation import Rotation

# Moves used in the case tables below, named after the notation they represent
X_CW: Move = Move(Rotation.X, Direction.CW, 1)
X_CCW: Move = Move(Rotation.X, Direction.CCW, 1)
X2: Move = Move(Rotation.X, Direction.DOUBLE, 1)
Y_CW: Move = Move(Rotation.Y, Direction.CW, 1)
Y_CCW: Move = Move(Rotation.Y, Direction.CCW, 1)
Y2: Move = Move(Rotation.Y, Direction.DOUBLE, 1)
Z_CW: Move = Move(Rotation.Z, Direction.CW, 1)
Z_CCW: Move = Move(Rotation.Z, Direction.CCW, 1)
Z2: Move = Move(Rotation.Z, Direction.DOUBLE, 1)

# The layer every face name refers to in the identity orientation, and after a single whole-cube
# rotation from it. Worked out by hand from the rotation each move performs.
IDENTITY_LAYERS: dict[Layer, Layer] = {layer: layer for layer in Layer}
# fmt: off
X_CW_LAYERS: dict[Layer, Layer] = {
    Layer.UP: Layer.FRONT, Layer.DOWN: Layer.BACK, Layer.LEFT: Layer.LEFT, Layer.RIGHT: Layer.RIGHT,
    Layer.FRONT: Layer.DOWN, Layer.BACK: Layer.UP,
}
X_CCW_LAYERS: dict[Layer, Layer] = {
    Layer.UP: Layer.BACK, Layer.DOWN: Layer.FRONT, Layer.LEFT: Layer.LEFT, Layer.RIGHT: Layer.RIGHT,
    Layer.FRONT: Layer.UP, Layer.BACK: Layer.DOWN,
}
X2_LAYERS: dict[Layer, Layer] = {
    Layer.UP: Layer.DOWN, Layer.DOWN: Layer.UP, Layer.LEFT: Layer.LEFT, Layer.RIGHT: Layer.RIGHT,
    Layer.FRONT: Layer.BACK, Layer.BACK: Layer.FRONT,
}
Y_CW_LAYERS: dict[Layer, Layer] = {
    Layer.UP: Layer.UP, Layer.DOWN: Layer.DOWN, Layer.LEFT: Layer.FRONT, Layer.RIGHT: Layer.BACK,
    Layer.FRONT: Layer.RIGHT, Layer.BACK: Layer.LEFT,
}
Y_CCW_LAYERS: dict[Layer, Layer] = {
    Layer.UP: Layer.UP, Layer.DOWN: Layer.DOWN, Layer.LEFT: Layer.BACK, Layer.RIGHT: Layer.FRONT,
    Layer.FRONT: Layer.LEFT, Layer.BACK: Layer.RIGHT,
}
Y2_LAYERS: dict[Layer, Layer] = {
    Layer.UP: Layer.UP, Layer.DOWN: Layer.DOWN, Layer.LEFT: Layer.RIGHT, Layer.RIGHT: Layer.LEFT,
    Layer.FRONT: Layer.BACK, Layer.BACK: Layer.FRONT,
}
Z_CW_LAYERS: dict[Layer, Layer] = {
    Layer.UP: Layer.LEFT, Layer.DOWN: Layer.RIGHT, Layer.LEFT: Layer.DOWN, Layer.RIGHT: Layer.UP,
    Layer.FRONT: Layer.FRONT, Layer.BACK: Layer.BACK,
}
Z_CCW_LAYERS: dict[Layer, Layer] = {
    Layer.UP: Layer.RIGHT, Layer.DOWN: Layer.LEFT, Layer.LEFT: Layer.UP, Layer.RIGHT: Layer.DOWN,
    Layer.FRONT: Layer.FRONT, Layer.BACK: Layer.BACK,
}
Z2_LAYERS: dict[Layer, Layer] = {
    Layer.UP: Layer.DOWN, Layer.DOWN: Layer.UP, Layer.LEFT: Layer.RIGHT, Layer.RIGHT: Layer.LEFT,
    Layer.FRONT: Layer.FRONT, Layer.BACK: Layer.BACK,
}
# fmt: on

# Rotation sequences that reach every one of the 24 orientations from the identity: each of the six
# faces a cube can show on top, combined with each of the four ways it can be spun around the
# vertical axis once it is there.
# fmt: off
ORIENTATION_ROTATIONS: list[str] = [
    "",    "y",    "y2",    "y'",
    "x",   "x y",  "x y2",  "x y'",
    "x2",  "x2 y", "x2 y2", "x2 y'",
    "x'",  "x' y", "x' y2", "x' y'",
    "z",   "z y",  "z y2",  "z y'",
    "z'",  "z' y", "z' y2", "z' y'",
]
# fmt: on


class TestOrientationLayers:
    def test_default_is_the_identity(self) -> None:
        """
        Tests that the layers getter returns the identity mapping when no layers are given to the
        constructor.

        :return: None
        """

        # Assert
        assert Orientation().layers == IDENTITY_LAYERS

    def test_getter_returns_the_given_layers(self) -> None:
        """
        Tests that the layers getter returns the mapping given to the constructor.

        :return: None
        """

        # Mock the orientation
        orientation = Orientation(X_CW_LAYERS)

        # Assert
        assert orientation.layers == X_CW_LAYERS


class TestOrientationEq:
    # fmt: off
    @pytest.mark.parametrize(
        "layers, other_layers, expected", [
            (IDENTITY_LAYERS, IDENTITY_LAYERS, True),
            (X_CW_LAYERS,     X_CW_LAYERS,     True),
            (X_CW_LAYERS,     X_CCW_LAYERS,    False),
            (IDENTITY_LAYERS, X_CW_LAYERS,     False),
        ]
    )
    # fmt: on
    def test_success(self, layers: dict[Layer, Layer], other_layers: dict[Layer, Layer], expected: bool) -> None:
        """
        Tests the equality method of the Orientation class.

        :param layers: The layers of the first orientation
        :param other_layers: The layers of the second orientation
        :param expected: The expected result of the equality comparison
        :return: None
        """

        # Assert
        assert (Orientation(layers) == Orientation(other_layers)) == expected

    def test_different_type(self) -> None:
        """
        Tests the equality method of the Orientation class when compared to a different type.

        :return: None
        """

        # Assert
        assert Orientation() != "Not an Orientation"


class TestOrientationHash:
    def test_equal_orientations_hash_equal(self) -> None:
        """
        Tests that two Orientation objects built from equal but distinct layers dictionaries hash
        the same.

        :return: None
        """

        # Assert
        assert hash(Orientation(dict(X_CW_LAYERS))) == hash(Orientation(dict(X_CW_LAYERS)))

    def test_usable_as_a_dict_key(self) -> None:
        """
        Tests that an Orientation object can be used as a dictionary key, which `to_moves` relies on
        to record the sequence found for each orientation.

        :return: None
        """

        # Mock a dictionary keyed by orientation
        cache = {Orientation(): "identity"}

        # Assert
        assert cache[Orientation()] == "identity"


class TestOrientationRotate:
    # fmt: off
    @pytest.mark.parametrize(
        "move, expected_layers", [
            (X_CW,  X_CW_LAYERS),
            (X_CCW, X_CCW_LAYERS),
            (X2,    X2_LAYERS),
            (Y_CW,  Y_CW_LAYERS),
            (Y_CCW, Y_CCW_LAYERS),
            (Y2,    Y2_LAYERS),
            (Z_CW,  Z_CW_LAYERS),
            (Z_CCW, Z_CCW_LAYERS),
            (Z2,    Z2_LAYERS),
        ]
    )
    # fmt: on
    def test_from_identity(self, move: Move, expected_layers: dict[Layer, Layer]) -> None:
        """
        Tests that rotating the identity orientation by each of the nine whole-cube rotations
        produces the orientation that rotation holds a cube in.

        :param move: The whole-cube rotation to perform
        :param expected_layers: The expected layer every face name refers to afterward
        :return: None
        """

        # Assert
        assert Orientation().rotate(move).layers == expected_layers

    def test_composes_with_a_previous_rotation(self) -> None:
        """
        Tests that rotating an already-rotated orientation composes with it: rotating by `x` twice
        reaches the same orientation as a single `x2`.

        :return: None
        """

        # Assert
        assert Orientation().rotate(X_CW).rotate(X_CW) == Orientation(X2_LAYERS)

    def test_does_not_mutate_the_original_orientation(self) -> None:
        """
        Tests that rotating an orientation returns a new object and leaves the original untouched.

        :return: None
        """

        # Mock the orientation and rotate it
        orientation = Orientation()
        rotated = orientation.rotate(X_CW)

        # Assert
        assert orientation.layers == IDENTITY_LAYERS
        assert rotated is not orientation


class TestOrientationToMoves:
    def test_identity_orientation_yields_no_moves(self) -> None:
        """
        Tests that the identity orientation is held by an empty sequence of rotations.

        :return: None
        """

        # Assert
        assert Orientation().to_moves() == []

    def test_single_rotation_yields_itself(self) -> None:
        """
        Tests that the orientation reached by a single whole-cube rotation is held by that same
        rotation.

        :return: None
        """

        # Mock the orientation
        orientation = Orientation().rotate(X_CW)

        # Assert
        assert orientation.to_moves() == [X_CW]

    def test_two_same_axis_rotations_yield_the_double_turn(self) -> None:
        """
        Tests the docstring example: the orientation of `x` followed by `x` is written as `x2`.

        :return: None
        """

        # Mock the orientation
        orientation = Orientation.from_moves([X_CW, X_CW])

        # Assert
        assert orientation.to_moves() == [X2]

    # fmt: off
    @pytest.mark.parametrize("rotations", ORIENTATION_ROTATIONS)
    # fmt: on
    def test_round_trips_every_orientation(self, rotations: str) -> None:
        """
        Tests that every one of the 24 orientations survives a `to_moves` -> `from_moves` round trip,
        and that the sequence `to_moves` returns never holds more than two rotations and never
        repeats an axis, which is what makes it the shortest one.

        :param rotations: The whole-cube rotations, in standard notation, that reach the orientation
        :return: None
        """

        # Mock the orientation
        orientation = Orientation.from_moves(Algorithm.from_str(rotations).moves)

        # Act
        moves = orientation.to_moves()

        # Assert
        assert Orientation.from_moves(moves) == orientation
        assert len(moves) <= 2
        if len(moves) == 2:
            assert moves[0].layer != moves[1].layer


class TestOrientationFromMoves:
    def test_no_rotations_yields_the_identity(self) -> None:
        """
        Tests that an empty sequence of rotations leaves the cube in the identity orientation.

        :return: None
        """

        # Assert
        assert Orientation.from_moves([]) == Orientation()

    def test_single_rotation(self) -> None:
        """
        Tests that a single rotation reaches the orientation that rotation holds a cube in.

        :return: None
        """

        # Assert
        assert Orientation.from_moves([X_CW]) == Orientation(X_CW_LAYERS)

    def test_two_same_axis_rotations_combine(self) -> None:
        """
        Tests that two rotations on the same axis are performed one after the other: `x` followed by
        `x` reaches the same orientation as a single `x2`.

        :return: None
        """

        # Assert
        assert Orientation.from_moves([X_CW, X_CW]) == Orientation(X2_LAYERS)

    def test_sequence_is_applied_in_order(self) -> None:
        """
        Tests that the rotations are performed in the order given: `x` followed by `y` reaches a
        different orientation than `y` followed by `x`, since whole-cube rotations do not commute.

        :return: None
        """

        # Assert
        assert Orientation.from_moves([X_CW, Y_CW]) != Orientation.from_moves([Y_CW, X_CW])
