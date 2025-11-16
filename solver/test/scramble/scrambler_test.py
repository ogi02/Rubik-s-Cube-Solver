# Python imports
from typing import Callable
from unittest.mock import patch

import pytest

# Project imports
from rubik_cube_solver.cube_rotation.move import Move
from rubik_cube_solver.enums.Direction import Direction
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.scramble.scrambler import Scrambler


# fmt: off
@pytest.mark.parametrize(
    "cube_size, scramble_length", [
        (2, 8),
        (3, 20),
        (4, 40),
        (5, 60),
        (6, 80),
        (7, 100),
    ]
)
# fmt: on
def test_generate_scramble_success(scrambler: Scrambler, cube_size: int, scramble_length: int) -> None:
    """
    Tests generating a scramble for a cube of valid size.

    :param scrambler: Fixture of a Scrambler instance
    :param cube_size: Size of the cube
    :param scramble_length: Expected length of the scramble
    :return: None
    """

    # Predefine a sequence of moves
    move_sequence = [Move(Layer.UP, Direction.CW, 1)] * scramble_length

    # Patch
    with (
        patch.object(scrambler, "_generate_random_move", side_effect=move_sequence) as mock_random,
        patch.object(scrambler, "_is_valid_random_move", return_value=True) as mock_valid,
        patch.object(scrambler, "_should_append_to_previous_moves", return_value=True) as mock_append,
        patch.object(scrambler, "_get_scramble_length", return_value=scramble_length) as mock_length,
    ):

        # Call the method
        scramble = scrambler.generate_scramble(cube_size)

        # Assert
        assert scramble == move_sequence
        assert len(scramble) == scramble_length
        assert all(isinstance(m, Move) for m in scramble)

        assert mock_length.call_count == 1
        mock_length.assert_called_once_with(cube_size)
        assert mock_random.call_count == scramble_length
        mock_random.assert_called_with(cube_size)
        assert mock_valid.call_count == scramble_length
        assert mock_append.call_count == scramble_length


# fmt: off
@pytest.mark.parametrize(
    "cube_size, scramble_length", [
        (3, 1),
    ]
)
# fmt: on
def test_generate_scramble_invalid_random_move_success(
    scrambler: Scrambler, cube_size: int, scramble_length: int
) -> None:
    """
    Tests generating a scramble for a cube of valid size.

    :param scrambler: Fixture of a Scrambler instance
    :param cube_size: Size of the cube
    :param scramble_length: Expected length of the scramble
    :return: None
    """

    # Predefine a sequence of moves
    move_sequence = [Move(Layer.UP, Direction.CW, 1)] * (scramble_length + 1)

    # Patch
    with (
        patch.object(scrambler, "_generate_random_move", side_effect=move_sequence) as mock_random,
        patch.object(scrambler, "_is_valid_random_move", side_effect=[False, True]) as mock_valid,
        patch.object(scrambler, "_should_append_to_previous_moves", return_value=False) as mock_append,
        patch.object(scrambler, "_get_scramble_length", return_value=scramble_length) as mock_length,
    ):

        # Call the method
        scramble = scrambler.generate_scramble(cube_size)

        # Assert
        assert len(scramble) == scramble_length

        assert mock_length.call_count == 1
        mock_length.assert_called_once_with(cube_size)
        assert mock_random.call_count == scramble_length + 1
        mock_random.assert_called_with(cube_size)
        assert mock_valid.call_count == scramble_length + 1
        assert mock_append.call_count == scramble_length


# fmt: off
@pytest.mark.parametrize(
    "expected_exception_type, expected_exception", [
        (ValueError, "Cube size must be at least 2."),
    ]
)
# fmt: on
def test_generate_scramble_exception(
    scrambler: Scrambler, expected_exception_type: type[BaseException], expected_exception: str
) -> None:
    """
    Tests that generating a scramble for a cube with an invalid size raises an exception.

    :param scrambler: Fixture of a Scrambler instance
    :param expected_exception_type: The expected exception type
    :param expected_exception: The expected exception message
    :return: None
    """

    with pytest.raises(expected_exception_type, match=expected_exception):
        scrambler.generate_scramble(1)


# fmt: off
@pytest.mark.parametrize(
    "cube_size, expected_length", [
        (2, 8),
        (3, 20),
        (4, 40),
        (5, 60),
        (6, 80),
        (7, 100),
    ]
)
# fmt: on
def test_get_scramble_length_success(scrambler: Scrambler, cube_size: int, expected_length: int):
    """
    Tests getting the scramble length for different cube sizes.

    :param scrambler: Fixture of a Scrambler instance
    :param cube_size: Size of the cube
    :param expected_length: The expected scramble length
    :return: None
    """

    # Call the method
    scramble_length = scrambler._get_scramble_length(cube_size)

    # Assert
    assert scramble_length == expected_length


# fmt: off
@pytest.mark.parametrize(
    "expected_exception_type, expected_exception", [
        (ValueError, "Cube size must be at least 2."),
    ]
)
# fmt: on
def test_get_scramble_length_exception(
    scrambler: Scrambler, expected_exception_type: type[BaseException], expected_exception: str
) -> None:
    """
    Tests that getting a scramble length for a cube with an invalid size raises an exception.

    :param scrambler: Fixture of a Scrambler instance
    :param expected_exception_type: The expected exception type
    :param expected_exception: The expected exception message
    :return: None
    """

    with pytest.raises(expected_exception_type, match=expected_exception):
        scrambler._get_scramble_length(1)


# fmt: off
@pytest.mark.parametrize(
    "cube_size, layer, direction, layer_amount, expect_randint_called",
    [
        (2, Layer.UP,    Direction.CW,     1, False),
        (3, Layer.FRONT, Direction.CCW,    1, False),
        (4, Layer.RIGHT, Direction.DOUBLE, 2, False),
        (5, Layer.BACK,  Direction.CW,     1, False),
        (6, Layer.LEFT,  Direction.CCW,    3, False),
        (7, Layer.UP,    Direction.DOUBLE, 2, False),
    ],
)
# fmt: on
def test_generate_random_move_success(
    scrambler: Scrambler,
    cube_size: int,
    layer: Layer,
    direction: Direction,
    layer_amount: int,
    expect_randint_called: bool,
) -> None:
    """
    Tests the logic of generating random moves for different cube sizes.

    :param scrambler: Fixture of a Scrambler instance
    :param cube_size: Size of the cube
    :param layer: Mocked layer to be returned by random.choice
    :param direction: Mocked direction to be returned by random.choice
    :param layer_amount: Mocked layer amount to be returned by random.randint
    :param expect_randint_called: Whether random.randint is expected to be called
    :return: None
    """

    with (
        patch("rubik_cube_solver.scramble.scrambler.random.choice") as mock_choice,
        patch("rubik_cube_solver.scramble.scrambler.random.randint") as mock_randint,
    ):

        # Mock the random choices
        mock_choice.side_effect = [layer, direction]
        mock_randint.return_value = layer_amount

        # Call the method
        move = scrambler._generate_random_move(cube_size)

        # Assert
        assert isinstance(move, Move)
        assert move.layer == layer
        assert move.direction == direction
        assert move.layer_amount == layer_amount

        assert mock_choice.call_count == 2
        if expect_randint_called:
            mock_randint.assert_called_once_with(1, cube_size // 2)


# fmt: off
@pytest.mark.parametrize(
    "expected_exception_type, expected_exception", [
        (ValueError, "Cube size must be at least 2."),
    ]
)
# fmt: on
def test_generate_random_move_exception(
    scrambler: Scrambler, expected_exception_type: type[BaseException], expected_exception: str
) -> None:
    """
    Tests that generating a random move with invalid cube size raises an exception.

    :param scrambler: Fixture of a Scrambler instance
    :param expected_exception_type: The expected exception type
    :param expected_exception: The expected exception message
    :return: None
    """

    with pytest.raises(expected_exception_type, match=expected_exception):
        scrambler._generate_random_move(1)


# fmt: off
@pytest.mark.parametrize(
    "layer, direction, layer_amount, expected", [
        (Layer.UP,    Direction.CW,     1, False),
        (Layer.DOWN,  Direction.CCW,    2, False),
        (Layer.UP,    Direction.DOUBLE, 3, True),
        (Layer.DOWN,  Direction.CW,     4, True),
        (Layer.FRONT, Direction.CCW,    1, True),
        (Layer.BACK,  Direction.DOUBLE, 2, True),
        (Layer.FRONT, Direction.CW,     3, True),
        (Layer.BACK,  Direction.CCW,    4, True),
        (Layer.LEFT,  Direction.DOUBLE, 1, True),
        (Layer.RIGHT, Direction.CW,     2, True),
        (Layer.LEFT,  Direction.CCW,    3, True),
        (Layer.RIGHT, Direction.DOUBLE, 4, True),
    ]
)
# fmt: on
def test_is_valid_random_move_success(
    scrambler: Scrambler,
    generate_move: Callable[[Layer, Direction, int], Move],
    previous_moves: list[Move],
    layer: Layer,
    direction: Direction,
    layer_amount: int,
    expected: bool,
) -> None:
    """
    Tests whether a random move is valid based on previous moves.

    :param scrambler: Fixture of a Scrambler instance
    :param generate_move: Fixture to generate a move
    :param previous_moves: List of previous moves
    :param layer: The layer of the move to test
    :param direction: The direction of the move to test
    :param layer_amount: The layer amount of the move to test
    :param expected: The expected result
    :return: None
    """

    # Create the move to test
    move = generate_move(layer, direction, layer_amount)

    # Assert
    assert scrambler._is_valid_random_move(move, previous_moves) == expected


# fmt: off
@pytest.mark.parametrize(
    "layer, direction, layer_amount", [
        (Layer.UP, Direction.CW, 1)
    ]
)
# fmt: on
def test_is_valid_random_move_no_previous_moves_success(
    scrambler: Scrambler,
    generate_move: Callable[[Layer, Direction, int], Move],
    layer: Layer,
    direction: Direction,
    layer_amount: int,
) -> None:
    """
    Tests whether a random move is valid based on previous moves.

    :param scrambler: Fixture of a Scrambler instance
    :param generate_move: Fixture to generate a move
    :param layer: The layer of the move to test
    :param direction: The direction of the move to test
    :param layer_amount: The layer amount of the move to test
    :return: None
    """

    # Create the move to test
    move = generate_move(layer, direction, layer_amount)

    # Assert
    assert scrambler._is_valid_random_move(move, [])


# fmt: off
@pytest.mark.parametrize(
    "layer, direction, layer_amount, expected", [
        (Layer.UP,    Direction.CW,     1, True),
        (Layer.DOWN,  Direction.CCW,    2, True),
        (Layer.FRONT, Direction.DOUBLE, 1, False),
        (Layer.BACK,  Direction.CW,     2, False),
        (Layer.LEFT,  Direction.CCW,    1, False),
        (Layer.RIGHT, Direction.DOUBLE, 2, False),
    ]
)
# fmt: on
def test_should_append_to_previous_moves_success(
    scrambler: Scrambler,
    generate_move: Callable[[Layer, Direction, int], Move],
    previous_moves: list[Move],
    layer: Layer,
    direction: Direction,
    layer_amount: int,
    expected: bool,
) -> None:
    """
    Tests whether a move should be appended to the previous moves list based on axis comparison.

    :param scrambler: Fixture of a Scrambler instance
    :param generate_move: Fixture to generate a move
    :param previous_moves: List of previous moves
    :param layer: The layer of the move to test
    :param direction: The direction of the move to test
    :param layer_amount: The layer amount of the move to test
    :param expected: The expected result
    :return: None
    """

    # Create the move to test
    move = generate_move(layer, direction, layer_amount)

    # Assert
    assert scrambler._should_append_to_previous_moves(move, previous_moves) == expected


# fmt: off
@pytest.mark.parametrize(
    "layer, direction, layer_amount", [
        (Layer.UP, Direction.CW, 1)
    ]
)
# fmt: on
def test_should_append_to_previous_moves_no_previous_moves_success(
    scrambler: Scrambler,
    generate_move: Callable[[Layer, Direction, int], Move],
    layer: Layer,
    direction: Direction,
    layer_amount: int,
) -> None:
    """
    Tests whether a move should be appended to the previous moves list based on axis comparison.

    :param scrambler: Fixture of a Scrambler instance
    :param generate_move: Fixture to generate a move
    :param layer: The layer of the move to test
    :param direction: The direction of the move to test
    :param layer_amount: The layer amount of the move to test
    :return: None
    """

    # Create the move to test
    move = generate_move(layer, direction, layer_amount)

    # Assert
    assert not scrambler._should_append_to_previous_moves(move, [])
