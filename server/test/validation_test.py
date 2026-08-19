# Python imports
import pytest

# Project imports
from message_type import MessageType
from role import Role
from validation import validate_message


class TestValidateMessage:
    """
    Tests for validate_message.
    """

    # fmt: off
    @pytest.mark.parametrize(
        "message, expected_message_type", [
            (
                {
                    "type": "cube_state",
                    "data": {
                        "dimensions": 2,
                        "state": {
                            "UP": ["W", "W", "W", "W"],
                            "DOWN": ["Y", "Y", "Y", "Y"],
                            "LEFT": ["O", "O", "O", "O"],
                            "RIGHT": ["R", "R", "R", "R"],
                            "FRONT": ["G", "G", "G", "G"],
                            "BACK": ["B", "B", "B", "B"],
                        },
                    },
                },
                MessageType.CUBE_STATE,
            ),
            ({"type": "apply_moves", "data": {"moves": ["R", "U", "R'", "U'"]}}, MessageType.APPLY_MOVES),
            ({"type": "apply_moves", "data": {"moves": []}}, MessageType.APPLY_MOVES),
        ])
    # fmt: on
    def test_success(self, message: dict, expected_message_type: MessageType) -> None:
        """
        Tests that validate_message returns the resolved MessageType for valid solver messages.

        :param message: The message to validate
        :param expected_message_type: The expected resolved MessageType
        """

        # Assert
        assert validate_message(message, Role.SOLVER) == expected_message_type

    def test_invalid_unknown_type(self) -> None:
        """
        Tests that validate_message raises ValueError for an unknown message type.
        """

        with pytest.raises(ValueError) as exc_info:
            validate_message({"type": "unknown_type", "data": {}}, Role.SOLVER)

        # Assert
        assert str(exc_info.value) == "Unknown message type: unknown_type"

    def test_invalid_missing_type(self) -> None:
        """
        Tests that validate_message raises ValueError when the type field is missing.
        """

        with pytest.raises(ValueError) as exc_info:
            validate_message({"data": {}}, Role.SOLVER)

        # Assert
        assert str(exc_info.value) == "Unknown message type: None"

    def test_invalid_non_string_type(self) -> None:
        """
        Tests that validate_message raises ValueError when the type field is not a string.
        """

        with pytest.raises(ValueError) as exc_info:
            validate_message({"type": 123, "data": {}}, Role.SOLVER)

        # Assert
        assert str(exc_info.value) == "Unknown message type: 123"

    def test_invalid_disconnect(self) -> None:
        """
        Tests that validate_message rejects disconnect messages, since they must never be relayed.
        """

        with pytest.raises(ValueError) as exc_info:
            validate_message({"type": "disconnect"}, Role.SOLVER)

        # Assert
        assert str(exc_info.value) == "Message type disconnect must not be relayed"

    def test_invalid_sender_role(self) -> None:
        """
        Tests that validate_message rejects a message from a non-solver sender.
        """

        message = {"type": "apply_moves", "data": {"moves": []}}

        with pytest.raises(ValueError) as exc_info:
            validate_message(message, Role.VISUALIZER)

        # Assert
        assert str(exc_info.value) == "Sender role VISUALIZER is not permitted to send message type apply_moves"

    # fmt: off
    @pytest.mark.parametrize(
        "data", [
            "not-a-dict",
            None,
            [],
        ])
    # fmt: on
    def test_invalid_cube_state_data_not_dict(self, data: object) -> None:
        """
        Tests that validate_message rejects a cube_state message whose data field is not a dict.

        :param data: A non-dict data payload
        """

        with pytest.raises(ValueError) as exc_info:
            validate_message({"type": "cube_state", "data": data}, Role.SOLVER)

        # Assert
        assert str(exc_info.value) == f"cube_state data must be a dict, got {data!r}"

    # fmt: off
    @pytest.mark.parametrize(
        "dimensions", [
            "2",
            2.0,
            None,
            True,
        ])
    # fmt: on
    def test_invalid_cube_state_dimensions_not_int(self, dimensions: object) -> None:
        """
        Tests that validate_message rejects a cube_state message whose dimensions field is not an int,
        including a bool value, which is a disallowed subclass of int.

        :param dimensions: A non-int (or bool) dimensions value
        """

        message = {"type": "cube_state", "data": {"dimensions": dimensions, "state": {}}}

        with pytest.raises(ValueError) as exc_info:
            validate_message(message, Role.SOLVER)

        # Assert
        assert str(exc_info.value) == f"cube_state dimensions must be an int, got {dimensions!r}"

    # fmt: off
    @pytest.mark.parametrize(
        "dimensions", [
            0,
            1,
            -1,
        ])
    # fmt: on
    def test_invalid_cube_state_dimensions_too_small(self, dimensions: int) -> None:
        """
        Tests that validate_message rejects a cube_state message whose dimensions field is below 2.

        :param dimensions: A dimensions value below the minimum
        """

        message = {"type": "cube_state", "data": {"dimensions": dimensions, "state": {}}}

        with pytest.raises(ValueError) as exc_info:
            validate_message(message, Role.SOLVER)

        # Assert
        assert str(exc_info.value) == f"cube_state dimensions must be >= 2, got {dimensions!r}"

    # fmt: off
    @pytest.mark.parametrize(
        "state", [
            "not-a-dict",
            None,
            [],
        ])
    # fmt: on
    def test_invalid_cube_state_state_not_dict(self, state: object) -> None:
        """
        Tests that validate_message rejects a cube_state message whose state field is not a dict.

        :param state: A non-dict state payload
        """

        message = {"type": "cube_state", "data": {"dimensions": 2, "state": state}}

        with pytest.raises(ValueError) as exc_info:
            validate_message(message, Role.SOLVER)

        # Assert
        assert str(exc_info.value) == f"cube_state state must be a dict, got {state!r}"

    def test_invalid_cube_state_state_missing_side(self) -> None:
        """
        Tests that validate_message rejects a cube_state message whose state is missing a required side.
        """

        message = {
            "type": "cube_state",
            "data": {
                "dimensions": 2,
                "state": {
                    "UP": ["W", "W", "W", "W"],
                    "DOWN": ["Y", "Y", "Y", "Y"],
                    "LEFT": ["O", "O", "O", "O"],
                    "RIGHT": ["R", "R", "R", "R"],
                    "FRONT": ["G", "G", "G", "G"],
                },
            },
        }

        with pytest.raises(ValueError) as exc_info:
            validate_message(message, Role.SOLVER)

        # Assert
        assert "cube_state state keys must be exactly" in str(exc_info.value)

    def test_invalid_cube_state_state_extra_side(self) -> None:
        """
        Tests that validate_message rejects a cube_state message whose state has an unexpected extra side.
        """

        message = {
            "type": "cube_state",
            "data": {
                "dimensions": 2,
                "state": {
                    "UP": ["W", "W", "W", "W"],
                    "DOWN": ["Y", "Y", "Y", "Y"],
                    "LEFT": ["O", "O", "O", "O"],
                    "RIGHT": ["R", "R", "R", "R"],
                    "FRONT": ["G", "G", "G", "G"],
                    "BACK": ["B", "B", "B", "B"],
                    "EXTRA": ["X", "X", "X", "X"],
                },
            },
        }

        with pytest.raises(ValueError) as exc_info:
            validate_message(message, Role.SOLVER)

        # Assert
        assert "cube_state state keys must be exactly" in str(exc_info.value)

    # fmt: off
    @pytest.mark.parametrize(
        "side_value", [
            "not-a-list",
            None,
            ["W", "W", "W", 1],
            ["W", "W", "W", None],
        ])
    # fmt: on
    def test_invalid_cube_state_side_not_list_of_str(self, side_value: object) -> None:
        """
        Tests that validate_message rejects a cube_state message whose side value is not a list of str.

        :param side_value: A malformed side value
        """

        message = {
            "type": "cube_state",
            "data": {
                "dimensions": 2,
                "state": {
                    "UP": side_value,
                    "DOWN": ["Y", "Y", "Y", "Y"],
                    "LEFT": ["O", "O", "O", "O"],
                    "RIGHT": ["R", "R", "R", "R"],
                    "FRONT": ["G", "G", "G", "G"],
                    "BACK": ["B", "B", "B", "B"],
                },
            },
        }

        with pytest.raises(ValueError) as exc_info:
            validate_message(message, Role.SOLVER)

        # Assert
        assert str(exc_info.value) == f"cube_state state[{'UP'!r}] must be a list of str, got {side_value!r}"

    def test_invalid_cube_state_side_wrong_length(self) -> None:
        """
        Tests that validate_message rejects a cube_state message whose side list length does not
        match dimensions squared.
        """

        message = {
            "type": "cube_state",
            "data": {
                "dimensions": 2,
                "state": {
                    "UP": ["W", "W", "W"],
                    "DOWN": ["Y", "Y", "Y", "Y"],
                    "LEFT": ["O", "O", "O", "O"],
                    "RIGHT": ["R", "R", "R", "R"],
                    "FRONT": ["G", "G", "G", "G"],
                    "BACK": ["B", "B", "B", "B"],
                },
            },
        }

        with pytest.raises(ValueError) as exc_info:
            validate_message(message, Role.SOLVER)

        # Assert
        assert str(exc_info.value) == "cube_state state['UP'] must have length 4, got 3"

    # fmt: off
    @pytest.mark.parametrize(
        "data", [
            "not-a-dict",
            None,
            [],
        ])
    # fmt: on
    def test_invalid_apply_moves_data_not_dict(self, data: object) -> None:
        """
        Tests that validate_message rejects an apply_moves message whose data field is not a dict.

        :param data: A non-dict data payload
        """

        with pytest.raises(ValueError) as exc_info:
            validate_message({"type": "apply_moves", "data": data}, Role.SOLVER)

        # Assert
        assert str(exc_info.value) == f"apply_moves data must be a dict, got {data!r}"

    # fmt: off
    @pytest.mark.parametrize(
        "moves", [
            "not-a-list",
            None,
            [1, 2],
            ["R", 1],
        ])
    # fmt: on
    def test_invalid_apply_moves_moves_not_list_of_str(self, moves: object) -> None:
        """
        Tests that validate_message rejects an apply_moves message whose moves field is not a list of str.

        :param moves: A malformed moves value
        """

        message = {"type": "apply_moves", "data": {"moves": moves}}

        with pytest.raises(ValueError) as exc_info:
            validate_message(message, Role.SOLVER)

        # Assert
        assert str(exc_info.value) == f"apply_moves moves must be a list of str, got {moves!r}"
