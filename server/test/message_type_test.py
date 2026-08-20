# Python imports
import pytest

# Project imports
from message_type import MessageType


class TestMessageTypeFromStr:
    """
    Tests for MessageType.from_str.
    """

    # fmt: off
    @pytest.mark.parametrize(
        "label, expected_message_type", [
            ("cube_state",   MessageType.CUBE_STATE),
            ("apply_moves",  MessageType.APPLY_MOVES),
            ("disconnect",   MessageType.DISCONNECT),
        ])
    # fmt: on
    def test_success(self, label: str, expected_message_type: MessageType) -> None:
        """
        Tests that MessageType.from_str correctly converts strings to MessageType enums.

        :param label: The string representation of the message type
        :param expected_message_type: The expected MessageType enum member
        """

        # Assert
        assert MessageType.from_str(label) == expected_message_type

    def test_invalid_unknown_label(self) -> None:
        """
        Tests that MessageType.from_str raises ValueError for an unknown message type string.
        """

        with pytest.raises(ValueError) as exc_info:
            MessageType.from_str("unknown_type")

        # Assert
        assert str(exc_info.value) == "Unknown message type: unknown_type"

    # fmt: off
    @pytest.mark.parametrize(
        "label", [
            None,
            123,
            ["cube_state"],
            {"type": "cube_state"},
        ])
    # fmt: on
    def test_invalid_non_string_label(self, label: object) -> None:
        """
        Tests that MessageType.from_str raises ValueError for non-string input instead of crashing.

        :param label: A non-string value to attempt to convert
        """

        with pytest.raises(ValueError) as exc_info:
            MessageType.from_str(label)  # type: ignore

        # Assert
        assert str(exc_info.value) == f"Unknown message type: {label}"
