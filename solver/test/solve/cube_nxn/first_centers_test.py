# Python imports
import random
from typing import Callable

import pytest

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.cube_rotation.rotator import Rotator
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.scramble.scrambler import Scrambler
from rubik_cube_solver.solve.cube_nxn.first_centers import (
    FIRST_CENTERS_ORIENTATION_TABLE,
    alignment,
    block_turn,
    center_cells,
    center_color,
    center_positions,
    column_slice,
    down_extraction,
    fill_schedule,
    fixed_center_layer,
    front_column_clearing,
    front_release,
    layer_turn,
    line_insertion,
    relocation,
    rotation_turn,
    row_slice,
    staging_move,
    staging_rows,
    up_eviction,
    wanted_pieces,
    wide_turn,
)


def _center_count(cube: Cube, layer: Layer, color: Color) -> int:
    """
    Counts the center pieces of the given color on a face, by reading raw stickers rather than
    going through `search_center`, so the oracle is independent of the code it is verifying.

    :param cube: The Cube instance to read
    :param layer: The face to count on
    :param color: The color to count
    :return: The amount of center cells of that face showing that color
    """

    size = cube.size

    return sum(cube.layers[layer][row * size + col] == color for row, col in center_cells(size))


def _apply(cube: Cube, algorithm: str) -> None:
    """
    Applies an algorithm written in standard notation to a cube.

    :param cube: The Cube instance to turn
    :param algorithm: The algorithm in standard notation
    :return: None
    """

    Rotator(cube).apply(Algorithm.from_str(algorithm))


def _clear_faces(cube: Cube, color: Color) -> None:
    """
    Takes every center piece of the given color off the DOWN and the UP faces, the state a line is
    staged from.

    :param cube: The Cube instance to turn
    :param color: The color of the center being built
    :return: None
    """

    algorithm = down_extraction(cube, color)
    while algorithm:
        _apply(cube, algorithm)
        algorithm = down_extraction(cube, color)

    algorithm = up_eviction(cube, color)
    while algorithm:
        _apply(cube, algorithm)
        algorithm = up_eviction(cube, color)


class TestWideTurn:
    # fmt: off
    @pytest.mark.parametrize(
        "layer, depth, direction, expected", [
            (Layer.RIGHT, 1, "",   "R"),
            (Layer.RIGHT, 1, "'",  "R'"),
            (Layer.RIGHT, 2, "",   "Rw"),
            (Layer.RIGHT, 2, "2",  "Rw2"),
            (Layer.UP,    3, "'",  "3Uw'"),
            (Layer.LEFT,  4, "",   "4Lw"),
        ]
    )
    # fmt: on
    def test_success(self, layer: Layer, depth: int, direction: str, expected: str) -> None:
        """
        Tests that a block of layers is written the way the notation spells it: a single layer by
        the face alone, two layers with a `w`, and more with the amount in front of it.

        :param layer: The face to turn
        :param depth: The amount of layers to turn
        :param direction: The direction of the turn
        :param expected: The expected notation
        :return: None
        """

        # Assert
        assert wide_turn(layer, depth, direction) == expected


class TestRotationTurn:
    # fmt: off
    @pytest.mark.parametrize(
        "layer, direction, expected", [
            (Layer.RIGHT, "",   "x"),
            (Layer.RIGHT, "'",  "x'"),
            (Layer.RIGHT, "2",  "x2"),
            (Layer.LEFT,  "",   "x'"),
            (Layer.LEFT,  "'",  "x"),
            (Layer.LEFT,  "2",  "x2"),
            (Layer.UP,    "",   "y"),
            (Layer.DOWN,  "",   "y'"),
            (Layer.DOWN,  "'",  "y"),
        ]
    )
    # fmt: on
    def test_success(self, layer: Layer, direction: str, expected: str) -> None:
        """
        Tests that the rotation of a face whose axis runs the other way, LEFT and DOWN, is written
        with the direction flipped, so that it turns the cube the way that face turns.

        :param layer: The face whose direction the rotation follows
        :param direction: The direction of the turn
        :param expected: The expected notation
        :return: None
        """

        # Assert
        assert rotation_turn(layer, direction) == expected


class TestBlockTurn:
    # fmt: off
    @pytest.mark.parametrize(
        "size, layer, depth, direction, expected", [
            # Nothing to turn
            (4, Layer.RIGHT, 0, "",  ""),
            # Blocks the notation can name on their own
            (4, Layer.RIGHT, 1, "",  "R"),
            (4, Layer.RIGHT, 2, "",  "Rw"),
            (6, Layer.UP,    3, "'", "3Uw'"),
            # Blocks deeper than half the cube, turned from the far side
            (4, Layer.RIGHT, 3, "",  "x L"),
            (5, Layer.RIGHT, 3, "",  "x Lw"),
            (6, Layer.UP,    4, "'", "y' Dw'"),
            # The whole cube
            (4, Layer.RIGHT, 4, "",  "x"),
            (5, Layer.UP,    5, "2", "y2"),
        ]
    )
    # fmt: on
    def test_success(self, size: int, layer: Layer, depth: int, direction: str, expected: str) -> None:
        """
        Tests that a block of layers deeper than half the cube, which the notation cannot name, is
        written as a whole-cube rotation with the layers on the far side turned back.

        :param size: The cube size
        :param layer: The face to turn
        :param depth: The amount of layers to turn
        :param direction: The direction of the turn
        :param expected: The expected notation
        :return: None
        """

        # Assert
        assert block_turn(size, layer, depth, direction) == expected


class TestLayerTurn:
    # fmt: off
    @pytest.mark.parametrize(
        "size, layer, depth, direction, expected", [
            (4, Layer.RIGHT, 1, "",  "R"),
            (5, Layer.RIGHT, 2, "",  "Rw R'"),
            (5, Layer.RIGHT, 3, "",  "x Lw Rw'"),
            (6, Layer.UP,    4, "",  "y Dw 3Uw'"),
        ]
    )
    # fmt: on
    def test_success(self, size: int, layer: Layer, depth: int, direction: str, expected: str) -> None:
        """
        Tests that a single layer is written as the block ending at it followed by the block in
        front of it turned back.

        :param size: The cube size
        :param layer: The face the depth is counted from
        :param depth: The depth of the layer
        :param direction: The direction of the turn
        :param expected: The expected notation
        :return: None
        """

        # Assert
        assert layer_turn(size, layer, depth, direction) == expected

    # fmt: off
    @pytest.mark.parametrize("size", [4, 5, 6])
    @pytest.mark.parametrize("layer", [Layer.UP, Layer.DOWN, Layer.LEFT, Layer.RIGHT])
    @pytest.mark.parametrize("direction", ["", "'", "2"])
    # fmt: on
    def test_layers_compose_into_the_block(
        self, generate_cube: Callable[[int, str], Cube], size: int, layer: Layer, direction: str
    ) -> None:
        """
        Tests every single layer turn of a face against the real `Rotator`, rather than against the
        notation it is built from: turning the layers at depth 1 up to `depth` one at a time has to
        leave the cube exactly where the block turn of that depth leaves it, for every depth up to
        the whole cube.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param size: The cube size
        :param layer: The face the depth is counted from
        :param direction: The direction of the turn
        :return: None
        """

        for depth in range(1, size + 1):
            # Turn the layers one at a time and turn the block of the same depth on another cube
            layers = generate_cube(size, "")
            for single in range(1, depth + 1):
                _apply(layers, layer_turn(size, layer, single, direction))

            block = generate_cube(size, block_turn(size, layer, depth, direction))

            # Assert
            assert layers.layers == block.layers


class TestColumnSlice:
    # fmt: off
    @pytest.mark.parametrize("size", [4, 5, 6])
    @pytest.mark.parametrize("col", [1, 2])
    # fmt: on
    def test_carries_the_front_column_onto_up(
        self, generate_cube: Callable[[int, str], Cube], size: int, col: int
    ) -> None:
        """
        Tests that the slice of a column turns the way the RIGHT face turns: the FRONT column ends
        up on UP, the DOWN column on FRONT, and every other column of UP is left alone.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param size: The cube size
        :param col: The column of the FRONT face
        :return: None
        """

        # Generate the cube and turn the slice
        cube = generate_cube(size, "")
        _apply(cube, column_slice(size, col, ""))

        # Assert the column moved on
        for row in range(1, size - 1):
            assert center_color(cube, Layer.UP, row, col) == Color.GREEN
            assert center_color(cube, Layer.FRONT, row, col) == Color.YELLOW

        # Assert every other column of UP stayed where it was
        for row, other in center_cells(size):
            if other != col:
                assert center_color(cube, Layer.UP, row, other) == Color.WHITE


class TestRowSlice:
    # fmt: off
    @pytest.mark.parametrize("size", [4, 5, 6])
    @pytest.mark.parametrize("row", [1, 2])
    # fmt: on
    def test_carries_the_front_row_onto_left(
        self, generate_cube: Callable[[int, str], Cube], size: int, row: int
    ) -> None:
        """
        Tests that the slice of a row turns the way the UP face turns: the FRONT row ends up on
        LEFT, the RIGHT row on FRONT, and neither the UP nor the DOWN face is touched at all, which
        is what lets a piece be fetched while a center is being built on either of them.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param size: The cube size
        :param row: The row of the side faces
        :return: None
        """

        # Generate the cube and turn the slice
        cube = generate_cube(size, "")
        _apply(cube, row_slice(size, row, ""))

        # Assert the row moved on
        for col in range(size):
            assert cube.layers[Layer.LEFT][row * size + col] == Color.GREEN
            assert cube.layers[Layer.FRONT][row * size + col] == Color.RED

        # Assert the faces the center is built on were not touched
        assert cube.layers[Layer.UP] == [Color.WHITE] * size * size
        assert cube.layers[Layer.DOWN] == [Color.YELLOW] * size * size


class TestCenterPositions:
    # fmt: off
    @pytest.mark.parametrize(
        "size, row, col, expected", [
            # A 4x4 cube has a single position type, the x center
            (4, 1, 1, [(1, 1), (1, 2), (2, 2), (2, 1)]),
            # A 5x5 cube adds the + center
            (5, 1, 1, [(1, 1), (1, 3), (3, 3), (3, 1)]),
            (5, 1, 2, [(1, 2), (2, 3), (3, 2), (2, 1)]),
            # A 6x6 cube is the smallest with two obliques, which no turn ever swaps
            (6, 1, 2, [(1, 2), (2, 4), (4, 3), (3, 1)]),
            (6, 2, 1, [(2, 1), (1, 3), (3, 4), (4, 2)]),
        ]
    )
    # fmt: on
    def test_success(self, size: int, row: int, col: int, expected: list[tuple[int, int]]) -> None:
        """
        Tests that the four cells of a position type are returned in the order a clockwise turn of
        the face cycles them through.

        :param size: The cube size
        :param row: The row of the cell
        :param col: The column of the cell
        :param expected: The four cells of the position type, in clockwise order
        :return: None
        """

        # Assert
        assert center_positions(size, row, col) == expected

    # fmt: off
    @pytest.mark.parametrize("size", [4, 5, 6])
    # fmt: on
    def test_order_follows_a_face_turn(self, generate_cube: Callable[[int, str], Cube], size: int) -> None:
        """
        Tests the order against the real `Rotator`: after one clockwise turn of the UP face, the
        sticker of every cell of a position type is the one that used to lie on the cell before it.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param size: The cube size
        :return: None
        """

        # Generate a cube whose UP face carries stickers of every color, and turn it
        cube = generate_cube(size, "R U' F2 L B'")
        before = list(cube.layers[Layer.UP])
        _apply(cube, "U")

        # Assert
        for row, col in center_cells(size):
            positions = center_positions(size, row, col)
            for index, (target_row, target_col) in enumerate(positions):
                source_row, source_col = positions[index - 1]
                assert center_color(cube, Layer.UP, target_row, target_col) == before[source_row * size + source_col]


class TestCenterCells:
    # fmt: off
    @pytest.mark.parametrize(
        "size, expected", [
            (4, 4),
            (5, 8),
            (6, 16),
            (7, 24),
        ]
    )
    # fmt: on
    def test_success(self, size: int, expected: int) -> None:
        """
        Tests that every inner cell of a face is a center cell, except the fixed center of an odd
        cube, which never leaves its face.

        :param size: The cube size
        :param expected: The amount of center cells of a face
        :return: None
        """

        # Assert
        assert len(center_cells(size)) == expected

    # fmt: off
    @pytest.mark.parametrize(
        "size, fixed_center", [
            (5, (2, 2)),
            (7, (3, 3)),
        ]
    )
    # fmt: on
    def test_skips_the_fixed_center(self, size: int, fixed_center: tuple[int, int]) -> None:
        """
        Tests that the fixed center of an odd cube is not among the cells, since it never leaves its
        face and is therefore never searched for, staged or inserted.

        :param size: The cube size
        :param fixed_center: The cell of the fixed center
        :return: None
        """

        # Assert
        assert fixed_center not in center_cells(size)


class TestCenterColor:
    def test_success(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that a cell is read at the row and column it is named by.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate a solved cube and turn a single slice of it
        cube = generate_cube(4, "")
        _apply(cube, column_slice(4, 1, ""))

        # Assert
        assert center_color(cube, Layer.UP, 1, 1) == Color.GREEN
        assert center_color(cube, Layer.UP, 1, 2) == Color.WHITE


class TestFixedCenterLayer:
    # fmt: off
    @pytest.mark.parametrize(
        "algorithm, expected", [
            ("",   Layer.DOWN),
            ("x",  Layer.FRONT),
            ("x'", Layer.BACK),
            ("x2", Layer.UP),
            ("z",  Layer.LEFT),
            ("z'", Layer.RIGHT),
        ]
    )
    # fmt: on
    def test_success(self, generate_cube: Callable[[int, str], Cube], algorithm: str, expected: Layer) -> None:
        """
        Tests that the face carrying the yellow fixed center is found whatever orientation the cube
        was turned into.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param algorithm: The rotation applied to the cube
        :param expected: The face carrying the yellow fixed center
        :return: None
        """

        # Generate the cube
        cube = generate_cube(5, algorithm)

        # Assert
        assert fixed_center_layer(cube, Color.YELLOW) == expected

    def test_missing_color(self) -> None:
        """
        Tests that a cube no face of which carries the color raises a ValueError naming it.

        :return: None
        """

        # Build a cube showing a single color
        cube = Cube(5, {layer: [Color.GREEN] * 25 for layer in Layer})

        # Assert
        with pytest.raises(ValueError, match="No face has a yellow fixed center."):
            fixed_center_layer(cube, Color.YELLOW)


class TestFirstCentersOrientationTable:
    # fmt: off
    @pytest.mark.parametrize("algorithm", ["", "x", "x'", "x2", "z", "z'", "y"])
    # fmt: on
    def test_brings_the_face_to_up(self, generate_cube: Callable[[int, str], Cube], algorithm: str) -> None:
        """
        Tests every entry of the table against the real `Rotator`: whichever face of an odd cube the
        yellow fixed center was turned onto, its entry brings that face to UP, where the center is
        built.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param algorithm: The rotation applied to the cube
        :return: None
        """

        # Generate the cube and turn it by the entry of the face carrying the yellow fixed center
        cube = generate_cube(5, algorithm)
        _apply(cube, FIRST_CENTERS_ORIENTATION_TABLE[fixed_center_layer(cube, Color.YELLOW)])

        # Assert
        assert fixed_center_layer(cube, Color.YELLOW) == Layer.UP


class TestStagingRows:
    # fmt: off
    @pytest.mark.parametrize(
        "size, col, expected", [
            (4, 1, [1, 2]),
            (5, 1, [1, 2, 3]),
            # The middle column of an odd cube stages nothing in the row of the fixed center
            (5, 2, [1, 3]),
            (6, 2, [1, 2, 3, 4]),
            (7, 3, [1, 2, 4, 5]),
        ]
    )
    # fmt: on
    def test_success(self, size: int, col: int, expected: list[int]) -> None:
        """
        Tests that a column is staged in every inner row, except the row of the fixed center when
        the column is the middle one of an odd cube.

        :param size: The cube size
        :param col: The staging column
        :param expected: The rows a piece is staged in
        :return: None
        """

        # Assert
        assert staging_rows(size, col) == expected


class TestFillSchedule:
    # fmt: off
    @pytest.mark.parametrize(
        "size, expected", [
            (4, [(1, "2", ""), (2, "2", "")]),
            (5, [(2, "", "y"), (1, "2", ""), (3, "2", "")]),
            (6, [(1, "2", ""), (4, "2", ""), (2, "2", ""), (3, "2", "")]),
            (7, [(3, "", "y"), (1, "2", ""), (5, "2", ""), (2, "2", ""), (4, "2", "")]),
        ]
    )
    # fmt: on
    def test_success(self, size: int, expected: list[tuple[int, str, str]]) -> None:
        """
        Tests that the columns are filled in pairs that map onto each other under the `U2` turn of
        the insertion, each filled from the other, and that the middle column of an odd cube is
        filled first, through the middle row and a `y` rotation.

        :param size: The cube size
        :param expected: The staging column, U turn and follow-up rotation of every line
        :return: None
        """

        # Assert
        assert fill_schedule(size) == expected


class TestLineInsertion:
    # fmt: off
    @pytest.mark.parametrize("size", [4, 5, 6])
    @pytest.mark.parametrize("col", [1, 2])
    # fmt: on
    def test_leaves_the_down_face_untouched(
        self, generate_cube: Callable[[int, str], Cube], size: int, col: int
    ) -> None:
        """
        Tests the property the whole step rests on: an insertion pulls the DOWN column onto FRONT
        and puts it back, so every center piece of the face built on DOWN survives the center built
        on UP.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param size: The cube size
        :param col: The staging column
        :return: None
        """

        # Generate a scrambled cube and insert the staged column
        cube = generate_cube(size, "R U2 F' Lw B Uw' R2")
        before = [center_color(cube, Layer.DOWN, row, column) for row, column in center_cells(size)]
        _apply(cube, line_insertion(size, col, "2"))

        # Assert
        assert [center_color(cube, Layer.DOWN, row, column) for row, column in center_cells(size)] == before

    # fmt: off
    @pytest.mark.parametrize("size", [4, 5, 6])
    # fmt: on
    def test_inserts_the_column_and_parks_the_staging_column(
        self, generate_cube: Callable[[int, str], Cube], size: int
    ) -> None:
        """
        Tests that the staged column lands on the column the U turn carries it to, and that the
        column of UP the first slice parks on BACK is brought back exactly as it was.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param size: The cube size
        :return: None
        """

        # Generate a scrambled cube and insert the staged column
        cube = generate_cube(size, "Rw' U F2 Lw2 D B'")
        staged = [center_color(cube, Layer.FRONT, row, 1) for row in range(1, size - 1)]
        parked = [center_color(cube, Layer.UP, row, 1) for row in range(1, size - 1)]
        _apply(cube, line_insertion(size, 1, "2"))

        # Assert the staged column landed on the partner column, which `U2` turns upside down
        assert [center_color(cube, Layer.UP, row, size - 2) for row in range(size - 2, 0, -1)] == staged

        # Assert the parked column came back
        assert [center_color(cube, Layer.UP, row, 1) for row in range(1, size - 1)] == parked


class TestDownExtraction:
    def test_empty_face(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that nothing is returned when the DOWN face holds no piece of the color being built.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate a solved cube, whose DOWN face is yellow
        cube = generate_cube(4, "")

        # Assert
        assert down_extraction(cube, Color.WHITE) == ""

    # fmt: off
    @pytest.mark.parametrize("size", [4, 5, 6])
    # fmt: on
    def test_takes_one_piece_off_at_a_time(self, generate_cube: Callable[[int, str], Cube], size: int) -> None:
        """
        Tests that every algorithm takes exactly one piece of the color off the DOWN face, and that
        repeating it empties the face, over a batch of seeded random scrambles.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param size: The cube size
        :return: None
        """

        random.seed(0)
        for _ in range(10):
            # Generate a scrambled cube
            cube = generate_cube(size, str(Algorithm(Scrambler().generate_scramble(size))))

            # Take the pieces off one at a time
            algorithm = down_extraction(cube, Color.YELLOW)
            while algorithm:
                before = _center_count(cube, Layer.DOWN, Color.YELLOW)
                _apply(cube, algorithm)

                # Assert the face lost exactly one piece
                assert _center_count(cube, Layer.DOWN, Color.YELLOW) == before - 1

                algorithm = down_extraction(cube, Color.YELLOW)

            # Assert
            assert _center_count(cube, Layer.DOWN, Color.YELLOW) == 0


class TestFrontColumnClearing:
    def test_clean_column(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that nothing is returned when the column holds no piece of the color being built.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate a solved cube, whose FRONT face is green
        cube = generate_cube(4, "")

        # Assert
        assert front_column_clearing(cube, Color.WHITE, 1) == ""

    # fmt: off
    @pytest.mark.parametrize("size", [4, 5, 6])
    # fmt: on
    def test_empties_the_column(self, generate_cube: Callable[[int, str], Cube], size: int) -> None:
        """
        Tests that the column is emptied of the color one row at a time, so that an insertion made
        from it can only put pieces of another color onto the face being built.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param size: The cube size
        :return: None
        """

        random.seed(1)
        for _ in range(10):
            # Generate a scrambled cube
            cube = generate_cube(size, str(Algorithm(Scrambler().generate_scramble(size))))

            # Clear the column one piece at a time
            algorithm = front_column_clearing(cube, Color.WHITE, 1)
            while algorithm:
                _apply(cube, algorithm)
                algorithm = front_column_clearing(cube, Color.WHITE, 1)

            # Assert
            assert all(center_color(cube, Layer.FRONT, row, 1) != Color.WHITE for row in range(1, size - 1))


class TestUpEviction:
    def test_empty_face(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that nothing is returned when the UP face holds no piece of the color being built.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate a solved cube, whose UP face is white
        cube = generate_cube(4, "")

        # Assert
        assert up_eviction(cube, Color.YELLOW) == ""

    # fmt: off
    @pytest.mark.parametrize("size", [4, 5, 6])
    # fmt: on
    def test_empties_the_face(self, generate_cube: Callable[[int, str], Cube], size: int) -> None:
        """
        Tests that repeating the algorithm empties the UP face of the color being built, over a
        batch of seeded random scrambles.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param size: The cube size
        :return: None
        """

        random.seed(2)
        for _ in range(10):
            # Generate a scrambled cube
            cube = generate_cube(size, str(Algorithm(Scrambler().generate_scramble(size))))

            # Take the pieces off one algorithm at a time
            algorithm = up_eviction(cube, Color.WHITE)
            while algorithm:
                _apply(cube, algorithm)
                algorithm = up_eviction(cube, Color.WHITE)

            # Assert
            assert _center_count(cube, Layer.UP, Color.WHITE) == 0


class TestWantedPieces:
    def test_success(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that the pieces of a source face are returned together with the staging row each is
        wanted in, one entry per piece and row.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate a solved 4x4 cube, whose LEFT face carries all four orange center pieces
        cube = generate_cube(4, "")

        # Assert
        assert wanted_pieces(cube, Color.ORANGE, 1, [1, 2], Layer.LEFT) == [
            (1, (1, 1)),
            (1, (1, 2)),
            (1, (2, 1)),
            (1, (2, 2)),
            (2, (1, 1)),
            (2, (1, 2)),
            (2, (2, 1)),
            (2, (2, 2)),
        ]

    def test_other_faces(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that a face holding no piece of the color contributes nothing.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate a solved 4x4 cube
        cube = generate_cube(4, "")

        # Assert
        assert wanted_pieces(cube, Color.ORANGE, 1, [1, 2], Layer.BACK) == []


class TestAlignment:
    def test_lines_up_and_drags(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that the rows a turn lines up are reported together with the pieces its row slices
        would drag onto the FRONT face. A solved 4x4 has all four pieces of the single position type
        on one face, so two of them line up with the staging column and the other two are dragged
        along with them.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate a solved 4x4 cube
        cube = generate_cube(4, "")

        # Assert
        assert alignment(cube, Color.ORANGE, 1, [1, 2], Layer.LEFT, 0) == ([1, 2], [(1, 2), (2, 2)])

    def test_nothing_lines_up(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that a face holding no piece of the color lines up nothing and drags nothing.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate a solved 4x4 cube
        cube = generate_cube(4, "")

        # Assert
        assert alignment(cube, Color.ORANGE, 1, [1, 2], Layer.RIGHT, 0) == ([], [])


class TestRelocation:
    # fmt: off
    @pytest.mark.parametrize("size", [4, 5, 6])
    # fmt: on
    def test_moves_the_piece_and_keeps_the_staging_column(
        self, generate_cube: Callable[[int, str], Cube], size: int
    ) -> None:
        """
        Tests that a piece pushed onto another side face really leaves the face it was on, and that
        the staged column of the FRONT face is exactly where it was afterwards, which is what the
        turn of the FRONT face around the row slice is there for.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param size: The cube size
        :return: None
        """

        # Generate a solved cube and mark a single piece of the LEFT face
        cube = generate_cube(size, "")
        cube.layers[Layer.LEFT][1 * size + 1] = Color.RED

        staged = [center_color(cube, Layer.FRONT, row, 1) for row in range(1, size - 1)]
        _apply(cube, relocation(cube, 1, Layer.LEFT, (1, 1), []))

        # Assert the marked piece is gone from the LEFT face
        assert _center_count(cube, Layer.LEFT, Color.RED) == 0

        # Assert the staging column came through untouched
        assert [center_color(cube, Layer.FRONT, row, 1) for row in range(1, size - 1)] == staged

    def test_avoids_the_row_of_a_piece_staying_behind(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that the face is turned to a position where the pushed piece no longer shares its row
        with a piece that stays behind, so the slice separates the two instead of moving both.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate a solved cube and mark the two pieces that share a row of the LEFT face
        cube = generate_cube(4, "")
        cube.layers[Layer.LEFT][1 * 4 + 1] = Color.RED
        cube.layers[Layer.LEFT][1 * 4 + 2] = Color.RED

        _apply(cube, relocation(cube, 1, Layer.LEFT, (1, 1), [(1, 2)]))

        # Assert exactly one of the two left the face
        assert _center_count(cube, Layer.LEFT, Color.RED) == 1


class TestFrontRelease:
    def test_no_piece_on_front(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that nothing is returned when no wanted piece lies on the staging face.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate a solved 4x4 cube, whose FRONT face carries no orange piece
        cube = generate_cube(4, "")

        # Assert
        assert front_release(cube, Color.ORANGE, 1, [1, 2]) == ""

    # fmt: off
    @pytest.mark.parametrize(
        "row, missing", [
            # A piece in a row that is still waiting is pushed off by a plain row slice
            (1, [1, 2]),
            # A piece in a row that is already staged is pushed off around a turn of the FRONT face
            (1, [2]),
        ]
    )
    # fmt: on
    def test_pushes_the_piece_off_the_front_face(
        self, generate_cube: Callable[[int, str], Cube], row: int, missing: list[int]
    ) -> None:
        """
        Tests that a wanted piece lying on the staging face is moved off it, whether its row is
        still waiting for a piece of its own or has already been staged.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param row: The row the piece lies in
        :param missing: The rows of the staging column still waiting for a piece
        :return: None
        """

        # Generate a solved cube whose FRONT face carries a single orange piece, off the staging column
        cube = generate_cube(4, "")
        cube.layers[Layer.FRONT][row * 4 + 2] = Color.ORANGE

        _apply(cube, front_release(cube, Color.ORANGE, 1, missing))

        # Assert
        assert _center_count(cube, Layer.FRONT, Color.ORANGE) == 0


class TestStagingMove:
    def test_staged_column(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that nothing is returned once every row of the staging column carries the color.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate a solved 4x4 cube, whose FRONT face is green throughout
        cube = generate_cube(4, "")

        # Assert
        assert staging_move(cube, Color.GREEN, 1) == ""

    # fmt: off
    @pytest.mark.parametrize("size", [4, 5, 6])
    @pytest.mark.parametrize("col", [1, 2])
    # fmt: on
    def test_stages_the_whole_column(self, generate_cube: Callable[[int, str], Cube], size: int, col: int) -> None:
        """
        Tests that repeating the algorithm fills every staging row of the column with the color,
        over a batch of seeded random scrambles, with the DOWN and UP faces emptied first the way
        the step does it.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param size: The cube size
        :param col: The staging column
        :return: None
        """

        random.seed(3)
        for _ in range(5):
            # Generate a scrambled cube and empty the faces the pieces cannot be fetched from
            cube = generate_cube(size, str(Algorithm(Scrambler().generate_scramble(size))))
            _clear_faces(cube, Color.WHITE)

            # Stage the column one algorithm at a time
            algorithm = staging_move(cube, Color.WHITE, col)
            while algorithm:
                _apply(cube, algorithm)
                algorithm = staging_move(cube, Color.WHITE, col)

            # Assert
            assert all(center_color(cube, Layer.FRONT, row, col) == Color.WHITE for row in staging_rows(size, col))
