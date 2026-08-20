# Python imports
import pytest

# Project imports
from rubik_cube_websocket_client import messages


class TestCubeState:
    """
    Tests for cube_state.
    """

    # fmt: off
    @pytest.mark.parametrize(
        "dimensions, state", [
            (2, {"UP": ["white"] * 4, "DOWN": ["yellow"] * 4, "LEFT": ["orange"] * 4,
                 "RIGHT": ["red"] * 4, "FRONT": ["green"] * 4, "BACK": ["blue"] * 4}),
            (3, {"UP": ["white"] * 9, "DOWN": ["yellow"] * 9, "LEFT": ["orange"] * 9,
                 "RIGHT": ["red"] * 9, "FRONT": ["green"] * 9, "BACK": ["blue"] * 9}),
        ]
    )
    # fmt: on
    def test_success(self, dimensions: int, state: dict[str, list[str]]) -> None:
        """
        Tests that cube_state builds the exact expected envelope.

        :param dimensions: The size of the cube
        :param state: The cube state, mapping each side name to a list of sticker colors
        """

        # Call cube_state
        message = messages.cube_state(dimensions, state)

        # Assert
        assert message == {"type": "cube_state", "data": {"dimensions": dimensions, "state": state}}


class TestApplyMoves:
    """
    Tests for apply_moves.
    """

    # fmt: off
    @pytest.mark.parametrize(
        "moves", [
            [],
            ["R"],
            ["R", "U", "R'"],
        ]
    )
    # fmt: on
    def test_success(self, moves: list[str]) -> None:
        """
        Tests that apply_moves builds the exact expected envelope.

        :param moves: The moves to apply, in cube notation
        """

        # Call apply_moves
        message = messages.apply_moves(moves)

        # Assert
        assert message == {"type": "apply_moves", "data": {"moves": moves}}


class TestDisconnect:
    """
    Tests for disconnect.
    """

    def test_success(self) -> None:
        """
        Tests that disconnect builds the exact expected envelope.
        """

        # Call disconnect
        message = messages.disconnect()

        # Assert
        assert message == {"type": "disconnect"}
