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
from rubik_cube_solver.solve.center_search import CenterSearchResult
from rubik_cube_solver.solve.cube_nxn.centers import (
    CENTERS_BUILD_TABLE,
    CENTERS_GREEN_FRONT_TABLE,
    CENTERS_SOURCE_LAYER,
    CENTERS_STAGING_LAYER,
    CENTERS_WHITE_UP_TABLE,
    bar_column,
    bar_cost,
    bar_import,
    bar_move,
    bar_rows,
    cell_color,
    center_is_solved,
    column_transfer,
    displaced_line,
    extraction_lines,
    finished_kind,
    fixed_center_layer,
    hop_evict,
    is_placed,
    line_cells,
    line_insertion,
    line_pieces,
    middle_completion,
    pole_eviction,
    preserved_line,
    row_transfer,
    solved_lines,
    source_hop,
    target_extraction,
    target_line,
    turn_notation,
    unturned_line,
)
from rubik_cube_solver.solve.cube_nxn.notation import center_cells, center_positions

# The sizes every big cube test runs on, as the center search uses: one position type, the + center
# with the fixed center that is skipped, and the two obliques that are different pieces.
SIZES: tuple[int, ...] = (4, 5, 6)

# The two frames a center is built in: the face it is built on, and the way its finished lines run.
TARGETS: tuple[Layer, ...] = (Layer.RIGHT, Layer.DOWN)


def labelled(size: int) -> Cube:
    """
    Builds a cube whose every sticker carries its own label, so any permutation can be read back.

    :param size: The size of the cube
    :return: The labelled cube
    """

    cube = Cube(size)
    for layer in Layer:
        cube.layers[layer] = [f"{layer.value}{index}" for index in range(size * size)]

    return cube


def label(layer: Layer, size: int, row: int, col: int) -> str:
    """
    Returns the label a labelled cube gives to one cell of a face.

    :param layer: The face the cell is on
    :param size: The size of the cube
    :param row: The row of the cell
    :param col: The column of the cell
    :return: The label of the cell
    """

    return f"{layer.value}{row * size + col}"


def apply(cube: Cube, algorithm: str) -> Cube:
    """
    Applies an algorithm to a cube and hands the same cube back.

    :param cube: The Cube instance to turn
    :param algorithm: The algorithm in standard notation
    :return: The cube with the algorithm applied
    """

    Rotator(cube).apply(Algorithm.from_str(algorithm))

    return cube


def paint(cube: Cube, layer: Layer, cells: list[tuple[int, int]], color: Color) -> Cube:
    """
    Paints a set of cells of one face in a color, to build a state by hand.

    :param cube: The Cube instance to paint
    :param layer: The face to paint on
    :param cells: The cells to paint
    :param color: The color to paint them
    :return: The painted cube
    """

    for row, col in cells:
        cube.layers[layer][row * cube.size + col] = color

    return cube


def scrambled(size: int, seed: int) -> Cube:
    """
    Builds a scrambled cube of the given size, from a seed so a failure reproduces.

    :param size: The size of the cube
    :param seed: The seed of the scramble
    :return: The scrambled cube
    """

    random.seed(seed)
    cube = Cube(size)

    return apply(cube, str(Algorithm(Scrambler().generate_scramble(size))))


def clear_poles(cube: Cube, color: Color) -> Cube:
    """
    Swaps every piece of the color off the two faces a row slice never reaches, which is the state
    the first two centers leave the cube in before the third and the fourth are built on the side.

    A piece is swapped with the very same cell of a side face, so it keeps its position type and
    the four pieces of every type are still four.

    :param cube: The Cube instance to rearrange
    :param color: The color the poles are cleared of
    :return: The rearranged cube
    """

    size = cube.size
    for pole in (Layer.UP, Layer.DOWN):
        for row, col in center_cells(size):
            if cell_color(cube, pole, row, col) is not color:
                continue

            for side in (CENTERS_SOURCE_LAYER, CENTERS_STAGING_LAYER, Layer.FRONT, Layer.RIGHT):
                if cell_color(cube, side, row, col) is not color:
                    index = row * size + col
                    cube.layers[pole][index], cube.layers[side][index] = (
                        cube.layers[side][index],
                        cube.layers[pole][index],
                    )
                    break

    return cube


class TestTurnNotation:
    # fmt: off
    @pytest.mark.parametrize(
        "turns, expected", [
            (0,  ""),
            (1,  "B"),
            (2,  "B2"),
            (3,  "B'"),
            (4,  ""),
            (-1, "B'"),
        ]
    )
    # fmt: on
    def test_success(self, turns: int, expected: str) -> None:
        """
        Tests that a count of clockwise quarter turns becomes the notation of that turn, that four
        of them are no turn at all and that a negative count turns the other way.

        :param turns: The amount of clockwise quarter turns
        :param expected: The notation expected
        :return: None
        """

        # Assert
        assert turn_notation(Layer.BACK, turns) == expected


class TestCellColor:
    # fmt: off
    @pytest.mark.parametrize("cube_size", SIZES)
    # fmt: on
    def test_success(self, generate_cube: Callable[[int, str], Cube], cube_size: int) -> None:
        """
        Tests that a cell of a face is read at the flat index its row and column address.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param cube_size: The cube size
        :return: None
        """

        # Generate the cube
        cube = generate_cube(cube_size, "")
        paint(cube, Layer.UP, [(1, 2)], Color.RED)

        # Assert
        assert cell_color(cube, Layer.UP, 1, 2) is Color.RED
        assert cell_color(cube, Layer.UP, 2, 1) is Color.WHITE


class TestFixedCenterLayer:
    # fmt: off
    @pytest.mark.parametrize(
        "color, expected", [
            (Color.WHITE,  Layer.UP),
            (Color.YELLOW, Layer.DOWN),
            (Color.GREEN,  Layer.FRONT),
        ]
    )
    # fmt: on
    def test_success(self, generate_cube: Callable[[int, str], Cube], color: Color, expected: Layer) -> None:
        """
        Tests that the face carrying a color's fixed center is found on a solved odd cube.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param color: The color of the fixed center
        :param expected: The face expected to carry it
        :return: None
        """

        # Assert
        assert fixed_center_layer(generate_cube(5, ""), color) is expected

    def test_invalid_color(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that a cube whose fixed centers hold none of the color raises a ValueError naming it,
        which is what an even cube looks like: it has no fixed center at all.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube with no white fixed center left
        cube = generate_cube(5, "")
        for layer in Layer:
            paint(cube, layer, [(2, 2)], Color.RED)

        # Assert
        with pytest.raises(ValueError, match="No face has a white fixed center"):
            fixed_center_layer(cube, Color.WHITE)


class TestBarRows:
    # fmt: off
    @pytest.mark.parametrize(
        "cube_size, col, expected", [
            (4, 1, [1, 2]),
            (5, 1, [1, 2, 3]),
            (5, 2, [1, 3]),
            (6, 2, [1, 2, 3, 4]),
        ]
    )
    # fmt: on
    def test_success(self, cube_size: int, col: int, expected: list[int]) -> None:
        """
        Tests that a bar covers every row of its column, apart from the cell that is the fixed
        center of an odd cube and cannot be filled.

        :param cube_size: The cube size
        :param col: The staging column
        :param expected: The rows expected to hold a bar piece
        :return: None
        """

        # Assert
        assert bar_rows(cube_size, col) == expected


class TestTargetLine:
    # fmt: off
    @pytest.mark.parametrize(
        "target, expected", [
            (Layer.RIGHT, [(2, 1), (2, 2), (2, 3)]),
            (Layer.DOWN,  [(1, 2), (2, 2), (3, 2)]),
        ]
    )
    # fmt: on
    def test_success(self, target: Layer, expected: list[tuple[int, int]]) -> None:
        """
        Tests that a line of the RIGHT face is a row and a line of the DOWN face is a column, since
        the slice family that reaches each of them runs a different way around the cube.

        :param target: The face being built
        :param expected: The cells expected in the line
        :return: None
        """

        # Assert
        assert target_line(5, target, 2) == expected


class TestSolvedLines:
    # fmt: off
    @pytest.mark.parametrize("cube_size", SIZES)
    @pytest.mark.parametrize("target", TARGETS)
    # fmt: on
    def test_success(self, generate_cube: Callable[[int, str], Cube], cube_size: int, target: Layer) -> None:
        """
        Tests that only the lines carrying the color throughout are reported, on a face where one
        line has been painted and one of its cells then painted over.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param cube_size: The cube size
        :param target: The face being built
        :return: None
        """

        # Generate the cube
        cube = generate_cube(cube_size, "")
        paint(cube, target, center_cells(cube_size), Color.BLUE)
        paint(cube, target, target_line(cube_size, target, 1), Color.RED)

        # Assert
        assert solved_lines(cube, Color.RED, target) == [1]

        paint(cube, target, target_line(cube_size, target, 1)[:1], Color.BLUE)
        assert solved_lines(cube, Color.RED, target) == []


class TestCenterIsSolved:
    # fmt: off
    @pytest.mark.parametrize("cube_size", SIZES)
    # fmt: on
    def test_success(self, generate_cube: Callable[[int, str], Cube], cube_size: int) -> None:
        """
        Tests that a center counts as solved once every center cell of the face shows the color,
        and stops counting as solved when a single cell does not.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param cube_size: The cube size
        :return: None
        """

        # Generate the cube
        cube = generate_cube(cube_size, "")

        # Assert
        assert center_is_solved(cube, Color.RED, Layer.RIGHT)

        paint(cube, Layer.RIGHT, [(1, 1)], Color.BLUE)
        assert not center_is_solved(cube, Color.RED, Layer.RIGHT)


class TestPreservedLine:
    # fmt: off
    @pytest.mark.parametrize(
        "cube_size, solved, expected", [
            (4, [],        1),
            (4, [2],       2),
            (4, [1, 2],    None),
            (5, [],        1),
            (5, [3],       3),
            (5, [1, 3],    None),
            (6, [1, 4],    2),
            (6, [1, 3, 4], 3),
        ]
    )
    # fmt: on
    def test_success(self, cube_size: int, solved: list[int], expected: int | None) -> None:
        """
        Tests that the line kept by the next insertion is one whose opposite still has to be filled,
        that an already finished line is preferred, and that nothing is left to do this way once the
        middle line of an odd cube is the only one missing.

        :param cube_size: The cube size
        :param solved: The lines that already carry the color throughout
        :param expected: The line the insertion is expected to keep
        :return: None
        """

        # Assert
        assert preserved_line(cube_size, solved) == expected


class TestBarColumn:
    # fmt: off
    @pytest.mark.parametrize(
        "target, preserved, expected", [
            (Layer.RIGHT, 1, 1),
            (Layer.RIGHT, 4, 4),
            (Layer.DOWN,  1, 4),
            (Layer.DOWN,  4, 1),
        ]
    )
    # fmt: on
    def test_success(self, target: Layer, preserved: int, expected: int) -> None:
        """
        Tests which column of the staging face a bar is assembled in, which is the kept line itself
        for the RIGHT face and the line opposite it for the DOWN face.

        :param target: The face being built
        :param preserved: The line the insertion keeps
        :param expected: The staging column expected
        :return: None
        """

        # Assert
        assert bar_column(6, target, preserved) == expected


class TestRowTransfer:
    # fmt: off
    @pytest.mark.parametrize("cube_size", SIZES)
    @pytest.mark.parametrize("evict", ["", "'", "2"])
    # fmt: on
    def test_success(self, cube_size: int, evict: str) -> None:
        """
        Tests that a row transfer moves the source face's row onto the staging face and leaves the
        two faces the slice only passes through, and both poles, exactly as they were.

        :param cube_size: The cube size
        :param evict: The turn of the receiving face between the slices
        :return: None
        """

        # Turn the cube
        row = 1
        cube = apply(labelled(cube_size), row_transfer(cube_size, CENTERS_STAGING_LAYER, row, "", evict))
        untouched = labelled(cube_size)

        # Assert
        arrived = [
            col
            for col in range(1, cube_size - 1)
            if cell_color(cube, CENTERS_STAGING_LAYER, row, col) == label(CENTERS_SOURCE_LAYER, cube_size, row, col)
        ]

        assert len(arrived) >= cube_size - 3
        for layer in (Layer.FRONT, Layer.RIGHT, Layer.UP, Layer.DOWN):
            assert [cell_color(cube, layer, *cell) for cell in center_cells(cube_size)] == [
                cell_color(untouched, layer, *cell) for cell in center_cells(cube_size)
            ]


class TestColumnTransfer:
    # fmt: off
    @pytest.mark.parametrize("cube_size", SIZES)
    # fmt: on
    def test_success(self, cube_size: int) -> None:
        """
        Tests that a column transfer fetches a column off the DOWN face onto the staging face while
        leaving the UP and the FRONT faces exactly as they were, which is what lets the face built
        before this one survive.

        :param cube_size: The cube size
        :return: None
        """

        # Turn the cube
        cube = apply(labelled(cube_size), column_transfer(cube_size, CENTERS_STAGING_LAYER, 1, "'", ""))
        untouched = labelled(cube_size)

        # Assert
        staging = "".join(cube.layers[CENTERS_STAGING_LAYER])

        assert label(Layer.DOWN, cube_size, 1, 1) in staging
        for layer in (Layer.UP, Layer.FRONT):
            assert [cell_color(cube, layer, *cell) for cell in center_cells(cube_size)] == [
                cell_color(untouched, layer, *cell) for cell in center_cells(cube_size)
            ]


class TestLineInsertion:
    # fmt: off
    @pytest.mark.parametrize("cube_size", SIZES)
    @pytest.mark.parametrize("target", TARGETS)
    # fmt: on
    def test_success(self, generate_cube: Callable[[int, str], Cube], cube_size: int, target: Layer) -> None:
        """
        Tests that a finished bar ends up as a whole line of the face being built, that the line the
        insertion keeps is left where it is, and that no other face's center loses a piece of the
        color, by building a bar of one color on the staging face by hand and inserting it.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param cube_size: The cube size
        :param target: The face being built
        :return: None
        """

        # Generate the cube with a bar on the staging face
        preserved = 1
        column = bar_column(cube_size, target, preserved)
        cube = generate_cube(cube_size, "")
        paint(cube, target, center_cells(cube_size), Color.BLUE)
        paint(cube, target, target_line(cube_size, target, preserved), Color.ORANGE)
        paint(cube, CENTERS_STAGING_LAYER, [(row, column) for row in bar_rows(cube_size, column)], Color.RED)

        # Insert the bar
        apply(cube, line_insertion(cube_size, target, preserved))

        # Assert
        filled = cube_size - 1 - preserved

        assert all(cell_color(cube, target, *cell) is Color.RED for cell in target_line(cube_size, target, filled))
        assert all(
            cell_color(cube, target, *cell) is Color.ORANGE for cell in target_line(cube_size, target, preserved)
        )


class TestMiddleCompletion:
    # fmt: off
    @pytest.mark.parametrize("target", TARGETS)
    # fmt: on
    def test_success(self, generate_cube: Callable[[int, str], Cube], target: Layer) -> None:
        """
        Tests that the completion lays a bar assembled in the middle column of the staging face
        across the middle line of the face being built, which is the line no insertion can fill.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param target: The face being built
        :return: None
        """

        # Generate the cube with a bar in the middle column of the staging face
        cube_size, middle = 5, 2
        cube = generate_cube(cube_size, "")
        paint(cube, target, center_cells(cube_size), Color.BLUE)
        paint(cube, CENTERS_STAGING_LAYER, [(row, middle) for row in bar_rows(cube_size, middle)], Color.RED)

        # Complete the middle line
        apply(cube, middle_completion(cube_size, target))

        # Assert
        kind = finished_kind(cube_size, target, middle)
        cells = line_cells(cube_size, (kind, middle))

        assert all(cell_color(cube, target, *cell) is Color.RED for cell in cells if cell != (middle, middle))


class TestPoleEviction:
    # fmt: off
    @pytest.mark.parametrize("cube_size", SIZES)
    @pytest.mark.parametrize("seed", [0, 1, 2])
    # fmt: on
    def test_success(self, cube_size: int, seed: int) -> None:
        """
        Tests that every algorithm takes exactly one piece of the color off the UP face, so that
        repeating it empties the face rather than shuffling it, and that an empty face asks for no
        algorithm at all.

        :param cube_size: The cube size
        :param seed: The seed of the scramble
        :return: None
        """

        # Generate the cube
        cube = scrambled(cube_size, seed)
        before = sum(cell_color(cube, Layer.UP, *cell) is Color.WHITE for cell in center_cells(cube_size))

        # Evict every piece
        for expected in range(before, 0, -1):
            algorithm = pole_eviction(cube, Color.WHITE)
            assert algorithm

            apply(cube, algorithm)
            assert (
                sum(cell_color(cube, Layer.UP, *cell) is Color.WHITE for cell in center_cells(cube_size))
                == expected - 1
            )

        # Assert
        assert pole_eviction(cube, Color.WHITE) == ""


class TestBarImport:
    # fmt: off
    @pytest.mark.parametrize("cube_size", SIZES)
    @pytest.mark.parametrize("bar_col", [1, 2])
    # fmt: on
    def test_success(self, generate_cube: Callable[[int, str], Cube], cube_size: int, bar_col: int) -> None:
        """
        Tests that a piece lying anywhere on the source face is turned onto the cell the bar wants
        and handed to the staging face, whichever of the four cells of its position type it starts
        on, and that the pieces already in the bar are still there afterwards.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param cube_size: The cube size
        :param bar_col: The staging column the bar is assembled in
        :return: None
        """

        # Assert
        for row in bar_rows(cube_size, bar_col):
            for start in center_positions(cube_size, row, bar_col):
                cube = generate_cube(cube_size, "")
                paint(cube, CENTERS_SOURCE_LAYER, center_cells(cube_size), Color.BLUE)
                paint(cube, CENTERS_SOURCE_LAYER, [start], Color.RED)
                paint(cube, CENTERS_STAGING_LAYER, center_cells(cube_size), Color.BLUE)

                result = CenterSearchResult(CENTERS_SOURCE_LAYER, *start)
                apply(cube, bar_import(cube_size, row, bar_col, result))

                assert cell_color(cube, CENTERS_STAGING_LAYER, row, bar_col) is Color.RED


class TestUnturnedLine:
    # fmt: off
    @pytest.mark.parametrize(
        "line, turns, expected", [
            (("row", 1), 0, ("row", 1)),
            (("row", 1), 1, ("col", 1)),
            (("row", 1), 2, ("row", 4)),
            (("row", 1), 3, ("col", 4)),
            (("col", 1), 1, ("row", 4)),
            (("col", 1), 3, ("row", 1)),
        ]
    )
    # fmt: on
    def test_success(self, line: tuple[str, int], turns: int, expected: tuple[str, int]) -> None:
        """
        Tests that a quarter turn takes rows to columns and back and that a half turn takes a line
        to the one opposite it, which is what says where an algorithm writes on a turned face.

        :param line: The line written to
        :param turns: The amount of clockwise quarter turns the face was turned by
        :param expected: The line the written one is expected to come from
        :return: None
        """

        # Assert
        assert unturned_line(6, line, turns) == expected


class TestExtractionLines:
    # fmt: off
    @pytest.mark.parametrize(
        "evict, turns, expected", [
            ("",  0, [("row", 1), ("col", 1)]),
            ("'", 0, [("row", 1), ("col", 4)]),
            ("2", 0, [("row", 1), ("row", 4)]),
            ("",  1, [("col", 1), ("row", 4)]),
        ]
    )
    # fmt: on
    def test_success(self, evict: str, turns: int, expected: list[tuple[str, int]]) -> None:
        """
        Tests which lines of the staging face an extraction overwrites: the one the fetched row
        lands in and the one what that row displaced ends up in.

        :param evict: The turn of the staging face between the slices
        :param turns: The quarter turns the extraction is conjugated with
        :param expected: The lines expected to be overwritten
        :return: None
        """

        # Assert
        assert extraction_lines(6, 1, evict, turns) == expected


class TestBarCost:
    def test_success(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that a column other than the bar's costs nothing, that the bar's own column costs
        every piece it holds and that a row costs the one cell of the bar it crosses.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube with two pieces in the bar
        cube = generate_cube(6, "")
        paint(cube, CENTERS_STAGING_LAYER, center_cells(6), Color.BLUE)
        paint(cube, CENTERS_STAGING_LAYER, [(1, 2), (3, 2)], Color.RED)

        # Assert
        assert bar_cost(cube, Color.RED, 2, ("col", 1)) == 0
        assert bar_cost(cube, Color.RED, 2, ("col", 2)) == 2
        assert bar_cost(cube, Color.RED, 2, ("row", 1)) == 1
        assert bar_cost(cube, Color.RED, 2, ("row", 2)) == 0


class TestTargetExtraction:
    # fmt: off
    @pytest.mark.parametrize("cube_size", SIZES)
    @pytest.mark.parametrize("target", TARGETS)
    # fmt: on
    def test_success(self, generate_cube: Callable[[int, str], Cube], cube_size: int, target: Layer) -> None:
        """
        Tests that a piece of the color sitting on the face being built is fetched off it, and that
        the extraction reports what it costs the bar - nothing at all when the bar is still empty.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param cube_size: The cube size
        :param target: The face being built
        :return: None
        """

        # Generate the cube with one piece on the face being built
        cube = generate_cube(cube_size, "")
        paint(cube, target, center_cells(cube_size), Color.BLUE)
        paint(cube, target, [(1, 1)], Color.RED)
        paint(cube, CENTERS_STAGING_LAYER, center_cells(cube_size), Color.BLUE)

        # Extract the piece
        cost, algorithm = target_extraction(cube, Color.RED, target, 2, CenterSearchResult(target, 1, 1))
        apply(cube, algorithm)

        # Assert
        assert cost == 0
        assert all(cell_color(cube, target, *cell) is not Color.RED for cell in center_cells(cube_size))


class TestDisplacedLine:
    # fmt: off
    @pytest.mark.parametrize(
        "evict, expected", [
            ("",  ("col", 1)),
            ("'", ("col", 4)),
            ("2", ("row", 4)),
        ]
    )
    # fmt: on
    def test_success(self, evict: str, expected: tuple[str, int]) -> None:
        """
        Tests which line a transfer sends back to the face the row came from, which is what decides
        whether the hop gains anything.

        :param evict: The turn of the receiving face between the slices
        :param expected: The line expected to be sent back
        :return: None
        """

        # Assert
        assert displaced_line(6, 1, evict) == expected


class TestLineCells:
    # fmt: off
    @pytest.mark.parametrize(
        "line, expected", [
            (("row", 1), [(1, 1), (1, 2), (1, 3)]),
            (("col", 2), [(1, 2), (2, 2), (3, 2)]),
        ]
    )
    # fmt: on
    def test_success(self, line: tuple[str, int], expected: list[tuple[int, int]]) -> None:
        """
        Tests that a line covers the center cells of the face and not its outer ring.

        :param line: The line to read
        :param expected: The cells expected in the line
        :return: None
        """

        # Assert
        assert line_cells(5, line) == expected


class TestLinePieces:
    def test_success(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that only the cells of the line and only the pieces of the asked color are counted.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(5, "")
        paint(cube, Layer.BACK, center_cells(5), Color.BLUE)
        paint(cube, Layer.BACK, [(1, 1), (1, 3), (2, 1)], Color.RED)

        # Assert
        assert line_pieces(cube, Layer.BACK, Color.RED, ("row", 1)) == 2
        assert line_pieces(cube, Layer.BACK, Color.RED, ("col", 1)) == 2
        assert line_pieces(cube, Layer.BACK, Color.RED, ("col", 2)) == 0


class TestHopEvict:
    def test_success(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that the turn whose line hands back the fewest pieces of the color is chosen.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube, with the color only in the line a half turn would send back
        cube = generate_cube(6, "")
        paint(cube, CENTERS_SOURCE_LAYER, center_cells(6), Color.BLUE)
        paint(cube, CENTERS_SOURCE_LAYER, line_cells(6, ("row", 4)), Color.RED)

        # Assert
        assert hop_evict(cube, CENTERS_SOURCE_LAYER, Color.RED, (1, 1)) != "2"

    def test_middle_row(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that a half turn is never chosen on the middle row of an odd cube, where the line it
        hands back is the very row that has just arrived and the hop gets nowhere.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(5, "")
        paint(cube, CENTERS_SOURCE_LAYER, center_cells(5), Color.BLUE)

        # Assert
        assert hop_evict(cube, CENTERS_SOURCE_LAYER, Color.RED, (2, 1)) != "2"


class TestSourceHop:
    # fmt: off
    @pytest.mark.parametrize("cube_size", SIZES)
    @pytest.mark.parametrize("layer", [Layer.FRONT, CENTERS_STAGING_LAYER])
    # fmt: on
    def test_success(self, generate_cube: Callable[[int, str], Cube], cube_size: int, layer: Layer) -> None:
        """
        Tests that a piece anywhere but the source face is moved onto it, and that the hop off the
        staging face leaves the bar assembled there untouched.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param cube_size: The cube size
        :param layer: The face the piece lies on
        :return: None
        """

        # Generate the cube with a piece to fetch and a bar to protect
        bar_col = 1
        cube = generate_cube(cube_size, "")
        paint(cube, layer, center_cells(cube_size), Color.BLUE)
        paint(cube, layer, [(1, 2)], Color.RED)
        paint(cube, CENTERS_STAGING_LAYER, [(row, bar_col) for row in bar_rows(cube_size, bar_col)], Color.GREEN)

        # Hop the piece
        result = CenterSearchResult(layer, 1, 2)
        algorithm = source_hop(cube, Color.RED, Layer.RIGHT, bar_col, result)
        apply(cube, algorithm)

        # Assert
        assert any(cell_color(cube, CENTERS_SOURCE_LAYER, *cell) is Color.RED for cell in center_cells(cube_size))
        assert all(
            cell_color(cube, CENTERS_STAGING_LAYER, row, bar_col) is Color.GREEN for row in bar_rows(cube_size, bar_col)
        )

    def test_no_hop(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that a piece already sitting in the bar's own column is left alone, since moving it
        would take the bar apart and it is a piece the bar wants anyway.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Assert
        result = CenterSearchResult(CENTERS_STAGING_LAYER, 1, 2)

        assert source_hop(generate_cube(6, ""), Color.RED, Layer.RIGHT, 2, result) == ""


class TestFinishedKind:
    # fmt: off
    @pytest.mark.parametrize(
        "cube_size, target, bar_col, expected", [
            (6, Layer.RIGHT, 2, "row"),
            (6, Layer.DOWN,  2, "col"),
            (5, Layer.RIGHT, 1, "row"),
            (5, Layer.RIGHT, 2, "col"),
            (5, Layer.DOWN,  2, "row"),
        ]
    )
    # fmt: on
    def test_success(self, cube_size: int, target: Layer, bar_col: int, expected: str) -> None:
        """
        Tests that the finished lines run the way the insertions fill them, and the other way while
        the middle line of an odd cube is being assembled, since the face is turned a quarter first.

        :param cube_size: The cube size
        :param target: The face being built
        :param bar_col: The staging column the bar is assembled in
        :param expected: The kind of the finished lines expected
        :return: None
        """

        # Assert
        assert finished_kind(cube_size, target, bar_col) == expected


class TestIsPlaced:
    # fmt: off
    @pytest.mark.parametrize("cube_size", SIZES)
    # fmt: on
    def test_success(self, generate_cube: Callable[[int, str], Cube], cube_size: int) -> None:
        """
        Tests that a piece in a finished line of the face being built counts as placed and one
        beside it does not, and that a piece on any other face is never placed.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param cube_size: The cube size
        :return: None
        """

        # Generate the cube with one finished row
        cube = generate_cube(cube_size, "")
        paint(cube, Layer.RIGHT, center_cells(cube_size), Color.BLUE)
        paint(cube, Layer.RIGHT, line_cells(cube_size, ("row", 1)), Color.RED)

        # Assert
        assert is_placed(cube, Color.RED, Layer.RIGHT, CenterSearchResult(Layer.RIGHT, 1, 1), "row")
        assert not is_placed(cube, Color.RED, Layer.RIGHT, CenterSearchResult(Layer.RIGHT, 2, 1), "row")
        assert not is_placed(cube, Color.RED, Layer.RIGHT, CenterSearchResult(Layer.BACK, 1, 1), "row")


class TestBarMove:
    # fmt: off
    @pytest.mark.parametrize("cube_size", SIZES)
    @pytest.mark.parametrize("target", TARGETS)
    @pytest.mark.parametrize("seed", [0, 1, 2])
    # fmt: on
    def test_success(self, cube_size: int, target: Layer, seed: int) -> None:
        """
        Tests that repeating the move assembles a whole bar on the staging face out of a scrambled
        cube whose poles are already built, which is the state every bar is assembled in.

        :param cube_size: The cube size
        :param target: The face being built
        :param seed: The seed of the scramble
        :return: None
        """

        # Generate the cube and assemble a bar
        cube = clear_poles(scrambled(cube_size, seed), Color.RED)
        column = bar_column(cube_size, target, 1)

        algorithm = bar_move(cube, Color.RED, target, column)
        while algorithm:
            apply(cube, algorithm)
            algorithm = bar_move(cube, Color.RED, target, column)

        # Assert
        assert all(
            cell_color(cube, CENTERS_STAGING_LAYER, row, column) is Color.RED for row in bar_rows(cube_size, column)
        )

    # fmt: off
    @pytest.mark.parametrize("cube_size", SIZES)
    # fmt: on
    def test_invalid_state(self, generate_cube: Callable[[int, str], Cube], cube_size: int) -> None:
        """
        Tests that a bar the cube holds no piece for raises a ValueError naming the color, rather
        than looping on a piece it can never reach. It takes a state no build can produce: every
        piece of the type is already in a finished line of the face being built, so none of them is
        a piece the bar is short of, and the bar is still missing one.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param cube_size: The cube size
        :return: None
        """

        # Generate the cube with every piece of the color already placed
        cube = generate_cube(cube_size, "")
        for layer in Layer:
            paint(cube, layer, center_cells(cube_size), Color.BLUE)

        paint(cube, Layer.RIGHT, line_cells(cube_size, ("row", 1)), Color.RED)

        # Assert
        with pytest.raises(ValueError, match="No red center piece can be brought into the bar"):
            bar_move(cube, Color.RED, Layer.RIGHT, 1)


class TestCentersTables:
    def test_orientation_tables(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that the two orientation tables put an odd cube upright from any of the twenty-four
        ways it can be held: the white fixed center on UP and the green one on FRONT, which by the
        cube's own colour scheme leaves yellow on DOWN and red on RIGHT.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Assert
        for first in ("", "x", "x'", "x2", "y", "y'", "y2", "z", "z'", "z2"):
            for second in ("", "x", "y", "z", "x2", "y2", "z2"):
                cube = generate_cube(5, f"{first} {second}")
                apply(cube, CENTERS_WHITE_UP_TABLE[fixed_center_layer(cube, Color.WHITE)])
                apply(cube, CENTERS_GREEN_FRONT_TABLE[fixed_center_layer(cube, Color.GREEN)])

                assert fixed_center_layer(cube, Color.WHITE) is Layer.UP
                assert fixed_center_layer(cube, Color.GREEN) is Layer.FRONT
                assert fixed_center_layer(cube, Color.YELLOW) is Layer.DOWN
                assert fixed_center_layer(cube, Color.RED) is Layer.RIGHT

    def test_build_table(self) -> None:
        """
        Tests that the four centers are the four the step promises and that the turns between them
        add up to a full circle, so the cube ends the step in the orientation it was put in.

        :return: None
        """

        # Assert
        assert [color for color, _, _ in CENTERS_BUILD_TABLE] == [
            Color.WHITE,
            Color.YELLOW,
            Color.GREEN,
            Color.RED,
        ]

        cube = Cube(5)
        for _, rotation, _ in CENTERS_BUILD_TABLE:
            apply(cube, rotation)

        assert cube.layers == Cube(5).layers
