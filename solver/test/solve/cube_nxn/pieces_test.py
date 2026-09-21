# Python imports
from typing import Callable

import pytest

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.solve.center_search import CenterSearchResult
from rubik_cube_solver.solve.cube_nxn.centers import CENTERS_PLAN
from rubik_cube_solver.solve.cube_nxn.pieces import (
    CenterSticker,
    bar_rows,
    built_cells,
    fill_order,
    finished_centers,
    fixed_centers,
    in_first_half,
    line_cells,
    orbit_cells,
    protected,
    rank_candidates,
)
from rubik_cube_solver.solve.cube_nxn.routes import trial

YELLOW_PRIORITY: tuple[tuple[Layer, ...], ...] = CENTERS_PLAN[0].priority


class TestInFirstHalf:
    # fmt: off
    @pytest.mark.parametrize(
        "size, index, expected", [
            (4, 0, True),
            (4, 1, True),
            (4, 2, False),
            (4, 3, False),
            (6, 2, True),
            (6, 3, False),
        ]
    )
    # fmt: on
    def test_success(self, size: int, index: int, expected: bool) -> None:
        """
        Tests that the indices before the middle of a face are in its first half and the rest are not.

        :param size: The cube size
        :param index: The row or column index
        :param expected: Whether the index lies in the first half
        :return: None
        """

        # Assert
        assert in_first_half(size, index) is expected


class TestOrbitCells:
    # fmt: off
    @pytest.mark.parametrize(
        "size, cell, expected", [
            (4, (1, 1), [(1, 1), (1, 2), (2, 2), (2, 1)]),
            (6, (1, 2), [(1, 2), (2, 4), (4, 3), (3, 1)]),
            (6, (3, 2), [(3, 2), (2, 2), (2, 3), (3, 3)]),
        ]
    )
    # fmt: on
    def test_success(self, size: int, cell: tuple[int, int], expected: list[tuple[int, int]]) -> None:
        """
        Tests that the four cells of a position type are returned, starting at the given cell.

        :param size: The cube size
        :param cell: The cell the orbit starts at
        :param expected: The four cells, in order
        :return: None
        """

        # Assert
        assert orbit_cells(size, cell) == expected

    # fmt: off
    @pytest.mark.parametrize("quarters", [1, 2, 3])
    # fmt: on
    def test_clockwise_order(self, generate_cube: Callable[[int, str], Cube], quarters: int) -> None:
        """
        Tests that the order is the order a clockwise face turn carries a piece in: a piece painted
        on the first cell is found on the cell `quarters` places along after that many turns of UP.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param quarters: The number of clockwise quarter turns of UP
        :return: None
        """

        # Paint one piece
        cube = generate_cube(6, "")
        cells = orbit_cells(6, (3, 2))
        cube.layers[Layer.UP][3 * 6 + 2] = Color.RED

        # Turn UP
        turned = trial(cube, " ".join(["U"] * quarters))

        # Assert
        row, col = cells[quarters]
        assert turned.layers[Layer.UP][row * 6 + col] is Color.RED


class TestFillOrder:
    # fmt: off
    @pytest.mark.parametrize(
        "size, expected", [
            (4, [1, 2]),
            (6, [2, 3, 1, 4]),
            (8, [3, 4, 2, 5, 1, 6]),
        ]
    )
    # fmt: on
    def test_success(self, size: int, expected: list[int]) -> None:
        """
        Tests that the inner columns come inner pair first, and the left column of each pair first.

        :param size: The cube size
        :param expected: The columns in filling order
        :return: None
        """

        # Assert
        assert fill_order(size) == expected


class TestBarRows:
    # fmt: off
    @pytest.mark.parametrize(
        "size, expected", [
            (4, [2, 2]),
            (5, [3, 3]),
            (6, [3, 3, 4, 4]),
            (7, [4, 4, 5, 5]),
            (8, [4, 4, 5, 5, 6, 6]),
        ]
    )
    # fmt: on
    def test_success(self, size: int, expected: list[int]) -> None:
        """
        Tests that every lower-half row is staged in twice, innermost first, and that an odd cube's
        middle row is left out.

        :param size: The cube size
        :param expected: The staging rows, one per bar
        :return: None
        """

        # Assert
        assert bar_rows(size) == expected

    # fmt: off
    @pytest.mark.parametrize("size", [2, 3])
    # fmt: on
    def test_invalid_size(self, size: int) -> None:
        """
        Tests that a cube smaller than 4 raises a ValueError naming its size.

        :param size: The cube size
        :return: None
        """

        # Assert
        with pytest.raises(ValueError, match=f"Bars are staged only on cubes of size 4 or more, got size {size}"):
            bar_rows(size)


class TestLineCells:
    # fmt: off
    @pytest.mark.parametrize(
        "size, vertical, expected", [
            (5, False, [(2, 1), (2, 3)]),
            (5, True,  [(1, 2), (3, 2)]),
            (7, False, [(3, 2), (3, 4), (3, 1), (3, 5)]),
            (7, True,  [(2, 3), (4, 3), (1, 3), (5, 3)]),
        ]
    )
    # fmt: on
    def test_success(self, size: int, vertical: bool, expected: list[tuple[int, int]]) -> None:
        """
        Tests that the line runs through the middle of the face, across it or down it, without the
        fixed center, and is filled inner pair first and the left (upper) cell of each pair first.

        :param size: The cube size
        :param vertical: Whether the line runs down the face
        :param expected: The cells, in filling order
        :return: None
        """

        # Assert
        assert line_cells(size, vertical) == expected


class TestBuiltCells:
    # fmt: off
    @pytest.mark.parametrize(
        "target, inserted, expected_lines", [
            (Layer.RIGHT, [],           set()),
            (Layer.RIGHT, [3],          {3}),
            (Layer.LEFT,  [3, 3],       {2, 3}),
            (Layer.DOWN,  [3, 3, 4],    {2, 3, 4}),
            (Layer.DOWN,  [3, 3, 4, 4], {1, 2, 3, 4}),
        ]
    )
    # fmt: on
    def test_success(self, target: Layer, inserted: list[int], expected_lines: set[int]) -> None:
        """
        Tests that a row staged once fills its own line and a row staged twice also fills its mirror,
        each line being a row of LEFT and RIGHT and a column of DOWN.

        :param target: The face the center is built on
        :param inserted: The staging rows of the bars inserted so far
        :param expected_lines: The lines of the target expected to be finished
        :return: None
        """

        # Work out the expected cells
        inner = range(1, 5)
        if target is Layer.DOWN:
            expected = {(row, line) for line in expected_lines for row in inner}
        else:
            expected = {(line, col) for line in expected_lines for col in inner}

        # Assert
        assert built_cells(6, target, inserted) == expected


class TestRankCandidates:
    def test_success(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that the pieces come in the order of their faces in the priority, so the BACK pieces of
        the first tier come before the RIGHT pieces of the second.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube: yellow's upper half stays on RIGHT and its lower half moves to BACK
        cube = generate_cube(4, "z' Dw")

        # Assert
        assert rank_candidates(cube, Color.YELLOW, (2, 1), YELLOW_PRIORITY, Layer.RIGHT, set()) == [
            CenterSearchResult(Layer.BACK, 2, 1),
            CenterSearchResult(Layer.BACK, 2, 2),
            CenterSearchResult(Layer.RIGHT, 1, 1),
            CenterSearchResult(Layer.RIGHT, 1, 2),
        ]

    def test_finished_cells_excluded(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that a piece in a finished cell of the target is not a candidate.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(4, "z' Dw")

        # Rank with row 1 of RIGHT finished
        ranked = rank_candidates(cube, Color.YELLOW, (2, 1), YELLOW_PRIORITY, Layer.RIGHT, {(1, 1), (1, 2)})

        # Assert
        assert ranked == [CenterSearchResult(Layer.BACK, 2, 1), CenterSearchResult(Layer.BACK, 2, 2)]

    def test_face_outside_priority_excluded(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that a piece on a face missing from the priority is not a candidate.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(4, "z' Dw")

        # Rank with only RIGHT as a source
        ranked = rank_candidates(cube, Color.YELLOW, (2, 1), ((Layer.RIGHT,),), Layer.RIGHT, set())

        # Assert
        assert [piece.layer for piece in ranked] == [Layer.RIGHT, Layer.RIGHT]


class TestProtected:
    def test_success(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that the bar cells earlier in the fill order, the inserted bar and the finished centers
        are protected, in that order.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(6, "")
        keep = [CenterSticker(Layer.UP, 1, 1, Color.WHITE)]

        # Assert
        assert protected(cube, Color.GREEN, (3, 1), Layer.RIGHT, [3], keep) == [
            CenterSticker(Layer.FRONT, 3, 2, Color.GREEN),
            CenterSticker(Layer.FRONT, 3, 3, Color.GREEN),
            CenterSticker(Layer.RIGHT, 3, 1, Color.GREEN),
            CenterSticker(Layer.RIGHT, 3, 2, Color.GREEN),
            CenterSticker(Layer.RIGHT, 3, 3, Color.GREEN),
            CenterSticker(Layer.RIGHT, 3, 4, Color.GREEN),
            CenterSticker(Layer.UP, 1, 1, Color.WHITE),
        ]

    def test_first_cell(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that nothing of the bar is protected for the first cell in the fill order, even where
        later cells already hold the colour.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(6, "")

        # Assert
        assert protected(cube, Color.GREEN, (3, 2), Layer.RIGHT, [], []) == []

    def test_earlier_cell_without_the_colour(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that an earlier bar cell is protected only while it holds the colour.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube and take the colour out of column 2
        cube = generate_cube(6, "")
        cube.layers[Layer.FRONT][3 * 6 + 2] = Color.RED

        # Assert
        assert protected(cube, Color.GREEN, (3, 1), Layer.RIGHT, [], []) == [
            CenterSticker(Layer.FRONT, 3, 3, Color.GREEN)
        ]


class TestFinishedCenters:
    def test_success(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that every cell of a face holding a finished colour is returned with that colour.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(4, "")

        # Assert
        assert finished_centers(cube, [Color.YELLOW]) == [
            CenterSticker(Layer.DOWN, 1, 1, Color.YELLOW),
            CenterSticker(Layer.DOWN, 1, 2, Color.YELLOW),
            CenterSticker(Layer.DOWN, 2, 1, Color.YELLOW),
            CenterSticker(Layer.DOWN, 2, 2, Color.YELLOW),
        ]

    # fmt: off
    @pytest.mark.parametrize(
        "algorithm, done", [
            # A uniform face whose colour is not finished
            ("",   []),
            # FRONT is never counted
            ("",   [Color.GREEN]),
            # A finished colour whose face is no longer uniform
            ("Rw", [Color.WHITE]),
        ]
    )
    # fmt: on
    def test_nothing_finished(
        self, generate_cube: Callable[[int, str], Cube], algorithm: str, done: list[Color]
    ) -> None:
        """
        Tests that a face counts only when its whole center is one colour, that colour is finished and
        the face is not FRONT.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param algorithm: The algorithm applied to a solved 4x4
        :param done: The colours whose centers are finished
        :return: None
        """

        # Generate the cube
        cube = generate_cube(4, algorithm)

        # Assert
        assert finished_centers(cube, done) == []


class TestFixedCenters:
    def test_success(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that the middle cell of every face is returned with the colour it holds, whichever
        colours have been moved there.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube: `x` carries each fixed center of the slice cycle one face on
        cube = generate_cube(5, "x")

        # Assert
        assert fixed_centers(cube) == [
            CenterSticker(Layer.UP, 2, 2, Color.GREEN),
            CenterSticker(Layer.DOWN, 2, 2, Color.BLUE),
            CenterSticker(Layer.LEFT, 2, 2, Color.ORANGE),
            CenterSticker(Layer.RIGHT, 2, 2, Color.RED),
            CenterSticker(Layer.FRONT, 2, 2, Color.YELLOW),
            CenterSticker(Layer.BACK, 2, 2, Color.WHITE),
        ]
