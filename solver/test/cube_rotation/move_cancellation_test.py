# Python imports
import pytest

# Project imports
from rubik_cube_solver.cube_rotation.move import Move
from rubik_cube_solver.cube_rotation.move_cancellation import can_combine, combine
from rubik_cube_solver.enums.Direction import Direction
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.enums.Rotation import Rotation

# Moves used in the case tables below, named after the notation they represent
R: Move = Move(Layer.RIGHT, Direction.CW, 1)
R_PRIME: Move = Move(Layer.RIGHT, Direction.CCW, 1)
R2: Move = Move(Layer.RIGHT, Direction.DOUBLE, 1)
U: Move = Move(Layer.UP, Direction.CW, 1)
RW: Move = Move(Layer.RIGHT, Direction.CW, 2)
RW_PRIME: Move = Move(Layer.RIGHT, Direction.CCW, 2)
RW2: Move = Move(Layer.RIGHT, Direction.DOUBLE, 2)
RW_3_LAYERS: Move = Move(Layer.RIGHT, Direction.CW, 3)
X: Move = Move(Rotation.X, Direction.CW, 1)
X_PRIME: Move = Move(Rotation.X, Direction.CCW, 1)
X2: Move = Move(Rotation.X, Direction.DOUBLE, 1)
Y: Move = Move(Rotation.Y, Direction.CW, 1)


class TestMoveCancellationCanCombine:
    # fmt: off
    @pytest.mark.parametrize(
        "first, second, expected", [
            (R,          R,           True),   # Same layer, same amount
            (R,          U,           False),  # Different layer
            (R,          RW,          False),  # Same layer, different amount
            (R,          X,           False),  # Layer versus rotation
            (X,          Y,           False),  # Two different rotations
            (X,          X_PRIME,     True),   # Same rotation
            (RW,         RW_PRIME,    True),   # Wide moves, same layer amount
            (RW,         RW_3_LAYERS, False),  # Wide moves, different layer amount
        ]
    )
    # fmt: on
    def test_success(self, first: Move, second: Move, expected: bool) -> None:
        """
        Tests that can_combine reports whether two moves name the same layer (or rotation axis)
        and the same layer amount.

        :param first: The first move
        :param second: The second move
        :param expected: The expected result
        :return: None
        """

        # Assert
        assert can_combine(first, second) == expected


class TestMoveCancellationCombine:
    # fmt: off
    @pytest.mark.parametrize(
        "first, second, expected", [
            (R,        R,        R2),       # CW + CW -> DOUBLE
            (R,        R_PRIME,  None),     # CW + CCW -> cancels out
            (R,        R2,       R_PRIME),  # CW + DOUBLE -> CCW
            (R_PRIME,  R_PRIME,  R2),       # CCW + CCW -> DOUBLE
            (R_PRIME,  R2,       R),        # CCW + DOUBLE -> CW
            (R2,       R2,       None),     # DOUBLE + DOUBLE -> cancels out
            (RW,       RW_PRIME, None),     # Wide moves cancel out
            (RW,       RW,       RW2),      # Wide moves keep their layer amount
            (X,        X_PRIME,  None),     # Rotations cancel out
            (X,        X,        X2),       # Rotations combine
        ]
    )
    # fmt: on
    def test_success(self, first: Move, second: Move, expected: Move | None) -> None:
        """
        Tests that combine returns the single move equivalent to performing `first` then `second`,
        or None when the two moves cancel each other out completely.

        :param first: The first move
        :param second: The second move
        :param expected: The expected combined move, or None if the moves cancel out
        :return: None
        """

        # Assert
        assert combine(first, second) == expected
