# Python imports
from typing import Callable

import pytest

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.cube_rotation.move import Move
from rubik_cube_solver.cube_rotation.rotator import Rotator
from rubik_cube_solver.enums.Direction import Direction
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.solve.cube_nxn.notation import (
    NOTATION_INVERSE_TABLE,
    NOTATION_OPPOSITE_TABLE,
    block_turn,
    center_cells,
    center_positions,
    column_slice,
    layer_turn,
    rotation_turn,
    row_slice,
    wide_turn,
)

# The sizes every big cube test runs on: a 4x4 has a single position type, a 5x5 adds the + center
# and the fixed center that is skipped, and a 6x6 is the smallest cube whose two obliques are
# different pieces and whose deepest layer cannot be named by a wide turn.
SIZES: tuple[int, ...] = (4, 5, 6)

DIRECTIONS: tuple[str, ...] = ("", "'", "2")


def painted(size: int) -> Cube:
    """
    Builds a cube whose every sticker carries its own label, so any permutation can be read back.

    :param size: The size of the cube
    :return: The labelled cube
    """

    cube = Cube(size)
    for layer in Layer:
        cube.layers[layer] = [f"{layer.value}{index}" for index in range(size * size)]

    return cube


def run(size: int, algorithm: str) -> Cube:
    """
    Applies an algorithm to a freshly labelled cube of the given size.

    :param size: The size of the cube
    :param algorithm: The algorithm in standard notation
    :return: The labelled cube with the algorithm applied
    """

    cube = painted(size)
    Rotator(cube).apply(Algorithm.from_str(algorithm))

    return cube


class TestWideTurn:
    # fmt: off
    @pytest.mark.parametrize(
        "depth, expected", [
            (1, "R"),
            (2, "Rw"),
            (3, "3Rw"),
        ]
    )
    # fmt: on
    def test_success(self, depth: int, expected: str) -> None:
        """
        Tests that the notation of a wide turn names as many layers as it turns, and that the move
        it produces parses back into exactly that amount of layers.

        :param depth: The amount of layers to turn
        :param expected: The notation expected for that depth
        :return: None
        """

        # Generate the notation
        notation = wide_turn(Layer.RIGHT, depth, "")

        # Assert
        assert notation == expected
        assert Move.from_str(notation).layer_amount == depth

    def test_direction(self) -> None:
        """
        Tests that the direction is carried through to the produced move.

        :return: None
        """

        # Assert
        assert Move.from_str(wide_turn(Layer.UP, 2, "'")).direction is Direction.CCW
        assert Move.from_str(wide_turn(Layer.UP, 2, "2")).direction is Direction.DOUBLE


class TestRotationTurn:
    # fmt: off
    @pytest.mark.parametrize("cube_size", SIZES)
    @pytest.mark.parametrize("layer", list(Layer))
    @pytest.mark.parametrize("direction", DIRECTIONS)
    # fmt: on
    def test_success(self, cube_size: int, layer: Layer, direction: str) -> None:
        """
        Tests that the rotation moves the whole cube and moves it the way the named face turns:
        every face of the turned cube carries the stickers of one face and one face only, and the
        face the rotation is named after ends up exactly as its own face turn leaves it.

        :param cube_size: The cube size
        :param layer: The face whose direction the rotation follows
        :param direction: The direction of the turn
        :return: None
        """

        # Turn the cube
        cube = run(cube_size, rotation_turn(layer, direction))

        # Assert
        for stickers in cube.layers.values():
            assert len({sticker[0] for sticker in stickers}) == 1

        assert cube.layers[layer] == run(cube_size, f"{layer.value}{direction}").layers[layer]


class TestBlockTurn:
    # fmt: off
    @pytest.mark.parametrize("cube_size", SIZES)
    @pytest.mark.parametrize("layer", list(Layer))
    @pytest.mark.parametrize("direction", DIRECTIONS)
    # fmt: on
    def test_shallow_block(self, cube_size: int, layer: Layer, direction: str) -> None:
        """
        Tests that a block the notation can name on its own is written as that plain wide turn.

        :param cube_size: The cube size
        :param layer: The face to turn
        :param direction: The direction of the turn
        :return: None
        """

        # Assert
        for depth in range(1, cube_size // 2 + 1):
            assert block_turn(cube_size, layer, depth, direction) == wide_turn(layer, depth, direction)

    # fmt: off
    @pytest.mark.parametrize("cube_size", SIZES)
    @pytest.mark.parametrize("layer", list(Layer))
    @pytest.mark.parametrize("direction", DIRECTIONS)
    # fmt: on
    def test_deep_block(self, cube_size: int, layer: Layer, direction: str) -> None:
        """
        Tests that a block deeper than half the cube, which no move may name, leaves the cube where
        turning every one of its layers on its own leaves it.

        :param cube_size: The cube size
        :param layer: The face to turn
        :param direction: The direction of the turn
        :return: None
        """

        # Assert
        for depth in range(1, cube_size + 1):
            expected = painted(cube_size)
            for single in range(1, depth + 1):
                Rotator(expected).apply(Algorithm.from_str(layer_turn(cube_size, layer, single, direction)))

            assert run(cube_size, block_turn(cube_size, layer, depth, direction)).layers == expected.layers

    # fmt: off
    @pytest.mark.parametrize("cube_size", SIZES)
    # fmt: on
    def test_no_layers(self, cube_size: int) -> None:
        """
        Tests that a block of no layers is no move at all.

        :param cube_size: The cube size
        :return: None
        """

        # Assert
        assert block_turn(cube_size, Layer.UP, 0, "") == ""


class TestLayerTurn:
    # fmt: off
    @pytest.mark.parametrize("cube_size", SIZES)
    @pytest.mark.parametrize("layer", list(Layer))
    @pytest.mark.parametrize("direction", DIRECTIONS)
    # fmt: on
    def test_outer_layers(self, cube_size: int, layer: Layer, direction: str) -> None:
        """
        Tests that the two layers the notation can already name - the face itself and the one on the
        far side of the cube - are turned exactly as their own face turn turns them.

        :param cube_size: The cube size
        :param layer: The face the depth is counted from
        :param direction: The direction of the turn
        :return: None
        """

        # Generate the far side turn
        opposite = NOTATION_OPPOSITE_TABLE[layer]
        far = f"{opposite.value}{NOTATION_INVERSE_TABLE[direction]}"

        # Assert
        assert (
            run(cube_size, layer_turn(cube_size, layer, 1, direction)).layers
            == run(cube_size, f"{layer.value}{direction}").layers
        )
        assert run(cube_size, layer_turn(cube_size, layer, cube_size, direction)).layers == run(cube_size, far).layers

    # fmt: off
    @pytest.mark.parametrize("cube_size", SIZES)
    @pytest.mark.parametrize("layer", list(Layer))
    # fmt: on
    def test_every_layer_is_the_whole_cube(self, cube_size: int, layer: Layer) -> None:
        """
        Tests that turning every layer of the cube one after the other is the whole-cube rotation,
        which is only true if each of them turns one layer and no other.

        :param cube_size: The cube size
        :param layer: The face the depths are counted from
        :return: None
        """

        # Turn every layer in turn
        cube = painted(cube_size)
        for depth in range(1, cube_size + 1):
            Rotator(cube).apply(Algorithm.from_str(layer_turn(cube_size, layer, depth, "")))

        # Assert
        assert cube.layers == run(cube_size, rotation_turn(layer, "")).layers


class TestRowSlice:
    # fmt: off
    @pytest.mark.parametrize("cube_size", SIZES)
    # fmt: on
    def test_success(self, cube_size: int) -> None:
        """
        Tests that a row slice carries the row of FRONT onto LEFT, of LEFT onto BACK, of BACK onto
        RIGHT and of RIGHT onto FRONT, keeping the row and column of every sticker, and that it
        leaves the UP and the DOWN faces alone.

        :param cube_size: The cube size
        :return: None
        """

        # Assert
        for row in range(1, cube_size - 1):
            cube = run(cube_size, row_slice(cube_size, row, ""))
            for col in range(cube_size):
                index = row * cube_size + col
                assert cube.layers[Layer.LEFT][index] == f"{Layer.FRONT.value}{index}"
                assert cube.layers[Layer.BACK][index] == f"{Layer.LEFT.value}{index}"
                assert cube.layers[Layer.RIGHT][index] == f"{Layer.BACK.value}{index}"
                assert cube.layers[Layer.FRONT][index] == f"{Layer.RIGHT.value}{index}"

            assert cube.layers[Layer.UP] == painted(cube_size).layers[Layer.UP]
            assert cube.layers[Layer.DOWN] == painted(cube_size).layers[Layer.DOWN]


class TestColumnSlice:
    # fmt: off
    @pytest.mark.parametrize("cube_size", SIZES)
    # fmt: on
    def test_success(self, cube_size: int) -> None:
        """
        Tests that a column slice carries the column of FRONT onto UP keeping its row and column,
        and that it leaves the LEFT and the RIGHT faces alone.

        :param cube_size: The cube size
        :return: None
        """

        # Assert
        for col in range(1, cube_size - 1):
            cube = run(cube_size, column_slice(cube_size, col, ""))
            for row in range(cube_size):
                index = row * cube_size + col
                assert cube.layers[Layer.UP][index] == f"{Layer.FRONT.value}{index}"
                assert cube.layers[Layer.FRONT][index] == f"{Layer.DOWN.value}{index}"

            assert cube.layers[Layer.LEFT] == painted(cube_size).layers[Layer.LEFT]
            assert cube.layers[Layer.RIGHT] == painted(cube_size).layers[Layer.RIGHT]


class TestCenterPositions:
    # fmt: off
    @pytest.mark.parametrize(
        "cube_size, row, col, expected", [
            (4, 1, 1, [(1, 1), (1, 2), (2, 2), (2, 1)]),
            (5, 1, 2, [(1, 2), (2, 3), (3, 2), (2, 1)]),
            (6, 1, 2, [(1, 2), (2, 4), (4, 3), (3, 1)]),
        ]
    )
    # fmt: on
    def test_success(self, cube_size: int, row: int, col: int, expected: list[tuple[int, int]]) -> None:
        """
        Tests that the four cells of a position type come back in the order a clockwise face turn
        cycles them through.

        :param cube_size: The cube size
        :param row: The row of the cell
        :param col: The column of the cell
        :param expected: The four cells in clockwise order
        :return: None
        """

        # Assert
        assert center_positions(cube_size, row, col) == expected

    # fmt: off
    @pytest.mark.parametrize("cube_size", SIZES)
    # fmt: on
    def test_matches_a_face_turn(self, generate_cube: Callable[[int, str], Cube], cube_size: int) -> None:
        """
        Tests the order against the real rotator: the sticker a clockwise turn of a face brings to a
        cell is the one that lay on the cell before it in the returned order.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param cube_size: The cube size
        :return: None
        """

        # Turn the face
        cube = run(cube_size, "R")

        # Assert
        for row, col in center_cells(cube_size):
            positions = center_positions(cube_size, row, col)
            source = positions[-1]
            assert cube.layers[Layer.RIGHT][row * cube_size + col] == f"R{source[0] * cube_size + source[1]}"


class TestCenterCells:
    # fmt: off
    @pytest.mark.parametrize(
        "cube_size, expected_count", [
            (4, 4),
            (5, 8),
            (6, 16),
        ]
    )
    # fmt: on
    def test_success(self, cube_size: int, expected_count: int) -> None:
        """
        Tests that every inner cell of a face is a center cell, apart from the fixed center of an
        odd cube, which never leaves the face it is on.

        :param cube_size: The cube size
        :param expected_count: The amount of center cells expected
        :return: None
        """

        # Generate the cells
        cells = center_cells(cube_size)
        middle = cube_size // 2

        # Assert
        assert len(cells) == expected_count
        assert all(1 <= row <= cube_size - 2 and 1 <= col <= cube_size - 2 for row, col in cells)
        assert ((middle, middle) in cells) == (cube_size % 2 == 0)
