# Python imports
from typing import Callable

import pytest

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.Direction import Direction
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.solve.center_search import CenterSearchResult, search_center
from rubik_cube_solver.solve.cube_nxn.pieces import orbit_cells
from rubik_cube_solver.solve.cube_nxn.routes import (
    across_routes,
    align_turn,
    column_slice,
    commutator_routes,
    cycle_routes,
    deep_move,
    direct_route,
    extraction,
    face_turns,
    front_insertion,
    insertion,
    inverse_of,
    lift,
    line_lift_routes,
    line_routes,
    line_target_routes,
    quarter_direction,
    staging_middle_routes,
    staging_routes,
    target_routes,
    trial,
    wide_depth,
    wide_moves,
)


def _marked_cube(size: int) -> Cube:
    """
    Returns a solved cube whose center cells are coloured in a pattern that no two faces share, so
    that any center moving from one cell to another is visible.

    :param size: The cube size
    :return: The marked cube
    """

    cube = Cube(size)
    colors = list(Color)

    for index, face in enumerate(Layer):
        for row in range(1, size - 1):
            for col in range(1, size - 1):
                cube.layers[face][row * size + col] = colors[(row * 7 + col * 3 + index) % 6]

    return cube


def _changed_centers(before: Cube, after: Cube) -> dict[Layer, set[tuple[int, int]]]:
    """
    Returns the center cells of every face whose colour differs between two cubes.

    :param before: The cube before an algorithm
    :param after: The cube after it
    :return: The changed center cells, per face that has any
    """

    size = before.size
    changed = {
        face: {
            (row, col)
            for row in range(1, size - 1)
            for col in range(1, size - 1)
            if before.layers[face][row * size + col] is not after.layers[face][row * size + col]
        }
        for face in Layer
    }

    return {face: cells for face, cells in changed.items() if cells}


class TestTrial:
    def test_success(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that the returned copy has the algorithm applied and the cube it was given does not.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(4, "")

        # Try an algorithm
        result = trial(cube, "R U")

        # Assert
        assert result.layers == generate_cube(4, "R U").layers
        assert cube.layers == Cube(4).layers


class TestInverseOf:
    # fmt: off
    @pytest.mark.parametrize(
        "notation, expected", [
            ("F'",        "F"),
            ("3Lw Lw'",   "Lw 3Lw'"),
            ("3Rw Rw' F", "F' Rw 3Rw'"),
            ("Lw2 U2",    "U2 Lw2"),
        ]
    )
    # fmt: on
    def test_success(self, generate_cube: Callable[[int, str], Cube], notation: str, expected: str) -> None:
        """
        Tests that the moves come in reverse order, each inverted, and that together they undo the
        algorithm on a cube.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param notation: The algorithm to invert
        :param expected: The inverse
        :return: None
        """

        # Generate the cube
        cube = generate_cube(6, "")

        # Assert
        assert inverse_of(notation) == expected
        assert trial(cube, f"{notation} {inverse_of(notation)}").layers == cube.layers


class TestQuarterDirection:
    # fmt: off
    @pytest.mark.parametrize(
        "quarters, expected", [
            (1, Direction.CW),
            (2, Direction.DOUBLE),
            (3, Direction.CCW),
            (5, Direction.CW),
            (7, Direction.CCW),
        ]
    )
    # fmt: on
    def test_success(self, quarters: int, expected: Direction) -> None:
        """
        Tests that a number of clockwise quarter turns maps onto the direction that performs them.

        :param quarters: The number of clockwise quarter turns
        :param expected: The direction
        :return: None
        """

        # Assert
        assert quarter_direction(quarters) is expected

    # fmt: off
    @pytest.mark.parametrize("quarters", [0, 4, 8])
    # fmt: on
    def test_invalid_quarters(self, quarters: int) -> None:
        """
        Tests that a multiple of four, which turns nothing, raises a ValueError naming the value.

        :param quarters: The number of quarter turns
        :return: None
        """

        # Assert
        with pytest.raises(ValueError, match=f"Invalid value {quarters} for a number of quarter turns"):
            quarter_direction(quarters)


class TestDeepMove:
    # fmt: off
    @pytest.mark.parametrize(
        "size, face, direction, depth, expected", [
            (5, Layer.RIGHT, Direction.CW,     2, "Rw"),
            (6, Layer.LEFT,  Direction.DOUBLE, 3, "3Lw2"),
            (5, Layer.RIGHT, Direction.CW,     3, "x Lw"),
            (5, Layer.DOWN,  Direction.CCW,    3, "y Uw'"),
            (5, Layer.BACK,  Direction.CW,     4, "z' F"),
            (7, Layer.UP,    Direction.CW,     5, "y Dw"),
        ]
    )
    # fmt: on
    def test_success(self, size: int, face: Layer, direction: Direction, depth: int, expected: str) -> None:
        """
        Tests that a block of at most half the cube is a wide move, and a deeper one the rotation that
        turns like the face followed by the opposite block turned the same way.

        :param size: The cube size
        :param face: The face the block is reached from
        :param direction: The direction, as seen from the face
        :param depth: The number of layers in the block
        :param expected: The turn
        :return: None
        """

        # Assert
        assert deep_move(size, face, direction, depth) == expected

    # fmt: off
    @pytest.mark.parametrize(
        "face, rotation, in_block", [
            (Layer.RIGHT, "x", lambda row, col: col >= 2),
            (Layer.LEFT,  "x'", lambda row, col: col <= 2),
            (Layer.UP,    "y", lambda row, col: row <= 2),
            (Layer.DOWN,  "y'", lambda row, col: row >= 2),
        ]
    )
    # fmt: on
    def test_turns_only_the_block(self, face: Layer, rotation: str, in_block: Callable[[int, int], bool]) -> None:
        """
        Tests that a block of three layers of a 5x5 turns its part of FRONT exactly as the whole-cube
        rotation turns it, and leaves the rest of FRONT where it was.

        :param face: The face the block is reached from
        :param rotation: The whole-cube rotation that turns like a clockwise turn of the face
        :param in_block: Whether a cell of FRONT lies in the block
        :return: None
        """

        # Mark the cube and turn the block, and the whole cube
        cube = _marked_cube(5)
        turned = trial(cube, deep_move(5, face, Direction.CW, 3))
        rotated = trial(cube, rotation)

        # Assert
        for index in range(25):
            expected = rotated if in_block(index // 5, index % 5) else cube
            assert turned.layers[Layer.FRONT][index] is expected.layers[Layer.FRONT][index]


class TestColumnSlice:
    # fmt: off
    @pytest.mark.parametrize(
        "size, col, direction, expected", [
            (6, 1, Direction.CW,     "Lw' L"),
            (6, 2, Direction.CW,     "3Lw' Lw"),
            (6, 3, Direction.CW,     "3Rw Rw'"),
            (6, 4, Direction.CW,     "Rw R'"),
            (6, 1, Direction.DOUBLE, "Lw2 L2"),
            (6, 4, Direction.CCW,    "Rw' R"),
            (5, 2, Direction.CW,     "x Lw Rw'"),
            (7, 3, Direction.CCW,    "x' 3Lw' 3Rw"),
        ]
    )
    # fmt: on
    def test_success(self, size: int, col: int, direction: Direction, expected: str) -> None:
        """
        Tests that the layer is reached from the nearer side, as the block ending at it followed by
        the block in front of it turned back, with the direction inverted from LEFT, and that the
        middle column of an odd cube is reached from RIGHT with a deep block.

        :param size: The cube size
        :param col: The column of FRONT
        :param direction: The direction, as seen from RIGHT
        :param expected: The turn
        :return: None
        """

        # Assert
        assert column_slice(size, col, direction) == expected

    # fmt: off
    @pytest.mark.parametrize(
        "size, col", [
            (6, 1),
            (6, 2),
            (6, 3),
            (6, 4),
            (5, 2),
            (7, 3),
        ]
    )
    # fmt: on
    def test_moves_only_its_column(self, size: int, col: int) -> None:
        """
        Tests that of FRONT only the column itself moves, and that the centers of LEFT and RIGHT do
        not move at all.

        :param size: The cube size
        :param col: The column of FRONT
        :return: None
        """

        # Mark the cube and turn the slice
        cube = _marked_cube(size)
        changed = _changed_centers(cube, trial(cube, column_slice(size, col, Direction.CW)))

        # Assert
        assert changed[Layer.FRONT] == {(row, col) for row in range(1, size - 1)}
        assert Layer.LEFT not in changed and Layer.RIGHT not in changed


class TestAlignTurn:
    # fmt: off
    @pytest.mark.parametrize(
        "layer, row, col, expected", [
            (Layer.UP,   3, 2, ""),
            (Layer.UP,   2, 2, "U'"),
            (Layer.UP,   2, 3, "U2"),
            (Layer.UP,   3, 3, "U"),
            (Layer.BACK, 3, 2, "B2"),
            (Layer.BACK, 2, 2, "B"),
            (Layer.BACK, 2, 3, ""),
            (Layer.BACK, 3, 3, "B'"),
            (Layer.DOWN, 3, 2, ""),
            (Layer.DOWN, 2, 2, "D'"),
            (Layer.DOWN, 2, 3, "D2"),
            (Layer.DOWN, 3, 3, "D"),
        ]
    )
    # fmt: on
    def test_success(self, layer: Layer, row: int, col: int, expected: str) -> None:
        """
        Tests that the source face is turned to the cell the slice collects from: the first cell of
        the orbit on UP and DOWN, and the third on BACK.

        :param layer: The face the piece is on
        :param row: The row of the piece
        :param col: The column of the piece
        :param expected: The turn
        :return: None
        """

        # Assert
        assert align_turn(6, (3, 2), CenterSearchResult(layer, row, col)) == expected


class TestDirectRoute:
    # fmt: off
    @pytest.mark.parametrize(
        "layer, row, col, restore, expected", [
            (Layer.UP,   2, 2, False, "U' 3Lw Lw'"),
            (Layer.UP,   2, 2, True,  "U' 3Lw Lw' F' Lw 3Lw' F"),
            (Layer.BACK, 2, 3, False, "3Lw2 Lw2"),
            (Layer.DOWN, 3, 2, False, "3Lw' Lw"),
            (Layer.UP,   3, 3, True,  "U 3Lw Lw' F' Lw 3Lw' F"),
        ]
    )
    # fmt: on
    def test_success(self, layer: Layer, row: int, col: int, restore: bool, expected: str) -> None:
        """
        Tests the route into FRONT (3, 2) of a 6x6 from each source face, bare and restoring.

        :param layer: The face the piece is on
        :param row: The row of the piece
        :param col: The column of the piece
        :param restore: Whether the slice is turned back
        :param expected: The route
        :return: None
        """

        # Assert
        assert direct_route(6, (3, 2), CenterSearchResult(layer, row, col), restore) == expected

    # fmt: off
    @pytest.mark.parametrize("layer", [Layer.UP, Layer.BACK, Layer.DOWN])
    @pytest.mark.parametrize("cell", [(3, 1), (3, 2), (3, 3), (4, 4)])
    @pytest.mark.parametrize("restore", [False, True])
    # fmt: on
    def test_delivers_the_piece(
        self, generate_cube: Callable[[int, str], Cube], layer: Layer, cell: tuple[int, int], restore: bool
    ) -> None:
        """
        Tests that a piece painted on any cell of the orbit on UP, BACK or DOWN arrives in the FRONT
        cell.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param layer: The face the piece is on
        :param cell: The FRONT cell to fill
        :param restore: Whether the slice is turned back
        :return: None
        """

        for row, col in orbit_cells(6, cell):
            # Paint one piece a colour no other face shows
            cube = generate_cube(6, "")
            cube.layers[layer][row * 6 + col] = Color.ORANGE

            # Bring it in
            result = trial(cube, direct_route(6, cell, CenterSearchResult(layer, row, col), restore))

            # Assert
            assert result.layers[Layer.FRONT][cell[0] * 6 + cell[1]] is Color.ORANGE

    # fmt: off
    @pytest.mark.parametrize("layer", [Layer.UP, Layer.BACK, Layer.DOWN])
    @pytest.mark.parametrize("cell", [(3, 1), (3, 2), (3, 3), (3, 4)])
    # fmt: on
    def test_restore_changes_only_front_and_source(self, layer: Layer, cell: tuple[int, int]) -> None:
        """
        Tests that the restoring form changes no center outside FRONT and the source face.

        :param layer: The face the piece is on
        :param cell: The FRONT cell to fill
        :return: None
        """

        # Mark the cube and run the route
        cube = _marked_cube(6)
        piece = CenterSearchResult(layer, *orbit_cells(6, cell)[1])
        changed = _changed_centers(cube, trial(cube, direct_route(6, cell, piece, True)))

        # Assert
        assert set(changed) <= {Layer.FRONT, layer}


class TestExtraction:
    # fmt: off
    @pytest.mark.parametrize(
        "size, side, row, over, expected", [
            (6, Layer.LEFT,  1, Direction.DOUBLE, "Uw B2 Uw'"),
            (6, Layer.RIGHT, 1, Direction.DOUBLE, "Uw' B2 Uw"),
            (6, Layer.RIGHT, 3, Direction.DOUBLE, "3Dw B2 3Dw'"),
            (6, Layer.LEFT,  4, Direction.CW,     "Dw' B Dw"),
            (5, Layer.LEFT,  2, Direction.CW,     "y Uw' B Uw y'"),
            (5, Layer.RIGHT, 2, Direction.CCW,    "y' Uw B' Uw' y"),
        ]
    )
    # fmt: on
    def test_success(self, size: int, side: Layer, row: int, over: Direction, expected: str) -> None:
        """
        Tests that the block reaches in from the nearer pole, as deep as the piece's row, turns
        towards BACK and turns back after BACK is turned, and that an odd cube's middle row is reached
        from DOWN with a deep block.

        :param size: The cube size
        :param side: The face the piece is on
        :param row: The row of the piece
        :param over: The direction BACK is turned
        :param expected: The conjugate
        :return: None
        """

        # Assert
        assert extraction(size, side, row, over) == expected

    # fmt: off
    @pytest.mark.parametrize("side", [Layer.LEFT, Layer.RIGHT])
    @pytest.mark.parametrize(
        "size, row, over", [
            (6, 1, Direction.DOUBLE),
            (6, 2, Direction.DOUBLE),
            (6, 3, Direction.DOUBLE),
            (6, 4, Direction.DOUBLE),
        ]
    )
    # fmt: on
    def test_moves_the_piece_to_back(self, side: Layer, size: int, row: int, over: Direction) -> None:
        """
        Tests that a piece painted on the side face ends on BACK, and that no center outside BACK and
        that side face moves.

        :param side: The face the piece is on
        :param size: The cube size
        :param row: The row of the piece
        :param over: The direction BACK is turned
        :return: None
        """

        # Paint one piece of the side face with the colour of UP, which the conjugate never changes
        cube = Cube(size)
        cube.layers[side][row * size + 1] = Color.WHITE
        marked = _marked_cube(size)
        route = extraction(size, side, row, over)

        # Assert
        parked = trial(cube, route)
        assert any(piece.layer is Layer.BACK for piece in search_center(parked, Color.WHITE, row, 1))
        assert set(_changed_centers(marked, trial(marked, route))) <= {Layer.BACK, side}

    # fmt: off
    @pytest.mark.parametrize("side", [Layer.LEFT, Layer.RIGHT])
    @pytest.mark.parametrize("col", [1, 3])
    # fmt: on
    def test_middle_row_needs_a_quarter_turn(self, side: Layer, col: int) -> None:
        """
        Tests that a piece in the middle row of an odd cube's side face comes back to the side face
        with a half turn of BACK and ends on BACK with one of the quarter turns, and that no center
        outside BACK and the side face moves.

        :param side: The face the piece is on
        :param col: The column of the piece
        :return: None
        """

        # Paint one piece in the middle row of the side face with the colour of UP
        cube = Cube(5)
        cube.layers[side][2 * 5 + col] = Color.WHITE
        marked = _marked_cube(5)

        # Park it with each turn of BACK
        parked = {
            over: [piece.layer for piece in search_center(trial(cube, extraction(5, side, 2, over)), Color.WHITE, 2, 1)]
            for over in Direction
        }

        # Assert
        assert Layer.BACK not in parked[Direction.DOUBLE]
        assert Layer.BACK in parked[Direction.CW] + parked[Direction.CCW]
        for over in Direction:
            assert set(_changed_centers(marked, trial(marked, extraction(5, side, 2, over)))) <= {Layer.BACK, side}


class TestAcrossRoutes:
    def test_success(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that for each turn of BACK - the half turn first - there is a bare and a restoring route
        per piece of the colour on BACK after the extraction, and that each of them fills the cell.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(4, "z' Dw")

        # Build the routes
        routes = across_routes(cube, Color.YELLOW, (2, 1), CenterSearchResult(Layer.RIGHT, 1, 1))

        # Assert
        assert routes[:4] == [
            "Uw' B2 Uw B2 Lw2 L2",
            "Uw' B2 Uw B2 Lw2 L2 F' L2 Lw2 F",
            "Uw' B2 Uw B' Lw2 L2",
            "Uw' B2 Uw B' Lw2 L2 F' L2 Lw2 F",
        ]
        assert [route.split()[1] for route in routes] == ["B2"] * 4 + ["B"] * 4 + ["B'"] * 4
        assert all(trial(cube, route).layers[Layer.FRONT][2 * 4 + 1] is Color.YELLOW for route in routes)

    def test_middle_row_piece(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that a piece in the middle row of an odd cube's side face, which a half turn of BACK
        cannot take out of the block, is brought in only by routes that turn BACK a quarter.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube: yellow is on RIGHT, and one of its pieces is swapped onto LEFT's middle row
        cube = generate_cube(5, "z'")
        cube.layers[Layer.LEFT][2 * 5 + 1] = Color.YELLOW
        cube.layers[Layer.RIGHT][1 * 5 + 2] = Color.WHITE

        # Build the routes
        routes = across_routes(cube, Color.YELLOW, (3, 2), CenterSearchResult(Layer.LEFT, 2, 1))

        # Assert
        assert routes
        assert all(route.split()[2] in ("B", "B'") for route in routes)


class TestLift:
    # fmt: off
    @pytest.mark.parametrize(
        "col, expected", [
            (1, "Lw2 U2 Lw2"),
            (2, "3Lw2 U2 3Lw2"),
            (3, "3Rw2 U2 3Rw2"),
            (4, "Rw2 U2 Rw2"),
        ]
    )
    # fmt: on
    def test_success(self, col: int, expected: str) -> None:
        """
        Tests that the block reaches in from the nearer side, as deep as the piece's column.

        :param col: The column of DOWN
        :param expected: The conjugate
        :return: None
        """

        # Assert
        assert lift(6, col, Direction.DOUBLE) == expected

    def test_middle_column(self) -> None:
        """
        Tests that the middle column of an odd cube is reached from RIGHT with a deep block, and that
        UP is turned the way asked.

        :return: None
        """

        # Assert
        assert lift(5, 2, Direction.CW) == "x2 Lw2 U x2 Lw2"

    # fmt: off
    @pytest.mark.parametrize("col", [1, 2, 3, 4])
    # fmt: on
    def test_moves_the_piece_to_up(self, col: int) -> None:
        """
        Tests that a piece painted on DOWN ends on UP, and that no center outside UP and DOWN moves.

        :param col: The column of DOWN
        :return: None
        """

        # Paint one piece of DOWN with a colour no face of a solved cube shows twice
        cube = Cube(6)
        cube.layers[Layer.DOWN][1 * 6 + col] = Color.BLUE
        marked = _marked_cube(6)
        route = lift(6, col, Direction.DOUBLE)

        # Assert
        assert any(piece.layer is Layer.UP for piece in search_center(trial(cube, route), Color.BLUE, 1, col))
        assert set(_changed_centers(marked, trial(marked, route))) <= {Layer.UP, Layer.DOWN}

    # fmt: off
    @pytest.mark.parametrize("row", [1, 3])
    # fmt: on
    def test_middle_column_needs_a_quarter_turn(self, row: int) -> None:
        """
        Tests that a piece in the middle column of an odd cube's DOWN stays on DOWN with a half turn of
        UP and ends on UP with one of the quarter turns, and that no center outside UP and DOWN moves.

        :param row: The row of the piece
        :return: None
        """

        # Paint one piece in the middle column of DOWN with the colour of LEFT, which the conjugate
        # never changes
        cube = Cube(5)
        cube.layers[Layer.DOWN][row * 5 + 2] = Color.ORANGE
        marked = _marked_cube(5)

        # Find where the piece lands with each turn of UP
        landed = {
            over: [piece.layer for piece in search_center(trial(cube, lift(5, 2, over)), Color.ORANGE, 1, 2)]
            for over in Direction
        }

        # Assert
        assert Layer.UP not in landed[Direction.DOUBLE]
        assert Layer.UP in landed[Direction.CW] + landed[Direction.CCW]
        for over in Direction:
            assert set(_changed_centers(marked, trial(marked, lift(5, 2, over)))) <= {Layer.UP, Layer.DOWN}


class TestTargetRoutes:
    def test_success(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that every route opens with the lift, that there is a bare and a restoring route per
        piece of the colour on UP afterwards, and that each of them fills the cell.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube: yellow is on DOWN
        cube = generate_cube(4, "")

        # Build the routes
        routes = target_routes(cube, Color.YELLOW, (2, 1), CenterSearchResult(Layer.DOWN, 1, 1))
        up_pieces = [
            piece
            for over in (Direction.DOUBLE, Direction.CW, Direction.CCW)
            for piece in search_center(trial(cube, lift(4, 1, over)), Color.YELLOW, 2, 1)
            if piece.layer is Layer.UP
        ]

        # Assert
        assert len(routes) == 2 * len(up_pieces)
        assert routes[0].startswith("Lw2 U2 Lw2 ")
        assert all(
            route.split()[:3] in (["Lw2", "U2", "Lw2"], ["Lw2", "U", "Lw2"], ["Lw2", "U'", "Lw2"]) for route in routes
        )
        assert all(trial(cube, route).layers[Layer.FRONT][2 * 4 + 1] is Color.YELLOW for route in routes)


class TestStagingRoutes:
    # fmt: off
    @pytest.mark.parametrize(
        "size, expected_count", [
            (4, 22),
            (6, 45),
            (8, 70),
        ]
    )
    # fmt: on
    def test_success(self, size: int, expected_count: int) -> None:
        """
        Tests that there is a commutator per column, slice direction and FRONT turn, and a long form
        per pair of depths, all of them different, with the commutators first.

        :param size: The cube size
        :param expected_count: The number of routes
        :return: None
        """

        # Build the routes
        routes = staging_routes(size)

        # Assert
        assert len(routes) == expected_count == len(set(routes))
        assert (
            routes[0] == f"F {column_slice(size, 1, Direction.CW)} F' {inverse_of(column_slice(size, 1, Direction.CW))}"
        )
        assert len(routes[-1].split()) == 9

    def test_long_form_changes_only_front_and_up(self) -> None:
        """
        Tests that every long form changes no center outside FRONT and UP.

        :return: None
        """

        # Mark the cube
        cube = _marked_cube(6)

        # Assert
        for route in staging_routes(6):
            if len(route.split()) == 9:
                assert set(_changed_centers(cube, trial(cube, route))) <= {Layer.FRONT, Layer.UP}


class TestInsertion:
    # fmt: off
    @pytest.mark.parametrize(
        "row, target, expected", [
            (3, Layer.RIGHT, "3Dw R2 3Dw' R2"),
            (4, Layer.RIGHT, "Dw R2 Dw' R2"),
            (3, Layer.LEFT,  "3Dw' L2 3Dw L2"),
            (3, Layer.DOWN,  "F' 3Rw' D2 3Rw D2"),
            (4, Layer.DOWN,  "F' Rw' D2 Rw D2"),
        ]
    )
    # fmt: on
    def test_success(self, row: int, target: Layer, expected: str) -> None:
        """
        Tests the insertion of a 6x6 bar into each target face.

        :param row: The row of FRONT holding the bar
        :param target: The face the center is built on
        :param expected: The algorithm
        :return: None
        """

        # Assert
        assert insertion(6, row, target) == expected

    # fmt: off
    @pytest.mark.parametrize("target", [Layer.LEFT, Layer.RIGHT, Layer.DOWN])
    @pytest.mark.parametrize("row", [3, 4])
    # fmt: on
    def test_bar_lands_on_its_line(self, target: Layer, row: int) -> None:
        """
        Tests that a bar painted in a FRONT row lands on the line of the target with the same index -
        a row of LEFT and RIGHT, a column of DOWN - and that no center outside FRONT and the target
        moves.

        :param target: The face the center is built on
        :param row: The row of FRONT holding the bar
        :return: None
        """

        # Paint the bar with the colour of BACK, which the insertion never changes
        cube = Cube(6)
        for col in range(1, 5):
            cube.layers[Layer.FRONT][row * 6 + col] = Color.BLUE
        marked = _marked_cube(6)

        # Insert it
        result = trial(cube, insertion(6, row, target))
        line = [(row, col) for col in range(1, 5)] if target is not Layer.DOWN else [(r, row) for r in range(1, 5)]

        # Assert
        assert all(result.layers[target][r * 6 + c] is Color.BLUE for r, c in line)
        assert set(_changed_centers(marked, trial(marked, insertion(6, row, target)))) <= {Layer.FRONT, target}

    # fmt: off
    @pytest.mark.parametrize("target", [Layer.UP, Layer.FRONT, Layer.BACK])
    # fmt: on
    def test_invalid_target(self, target: Layer) -> None:
        """
        Tests that a face no center is built on raises a ValueError naming it.

        :param target: The face
        :return: None
        """

        # Assert
        with pytest.raises(ValueError, match=f"Invalid value {target} for the face a center is built on"):
            insertion(6, 3, target)


class TestFaceTurns:
    def test_success(self) -> None:
        """
        Tests that no turn comes first, then the three turns of the face.

        :return: None
        """

        # Assert
        assert [str(turn) for turn in face_turns(Layer.DOWN)] == ["None", "D", "D'", "D2"]


class TestWideDepth:
    # fmt: off
    @pytest.mark.parametrize(
        "size, cell, expected", [
            (5, (2, 1), 2),
            (5, (3, 2), 2),
            (7, (3, 2), 3),
            (7, (3, 4), 3),
            (7, (1, 3), 2),
            (7, (3, 5), 2),
            (9, (4, 1), 2),
        ]
    )
    # fmt: on
    def test_success(self, size: int, cell: tuple[int, int], expected: int) -> None:
        """
        Tests that the block reaches from the nearer side exactly as far as the cell, on both sides
        of the fixed center and in both directions of the line.

        :param size: The cube size
        :param cell: The cell of the middle line
        :param expected: The depth
        :return: None
        """

        # Assert
        assert wide_depth(size, cell) == expected


class TestWideMoves:
    # fmt: off
    @pytest.mark.parametrize(
        "cell, target, source, expected_faces", [
            ((2, 1), Layer.RIGHT, Layer.FRONT, {"U", "D"}),
            ((2, 1), Layer.RIGHT, Layer.UP,    {"F", "B"}),
            ((2, 1), Layer.RIGHT, Layer.LEFT,  {"U", "D", "F", "B"}),
            ((1, 2), Layer.DOWN,  None,        {"F", "B", "L", "R"}),
        ]
    )
    # fmt: on
    def test_success(
        self, cell: tuple[int, int], target: Layer, source: Layer | None, expected_faces: set[str]
    ) -> None:
        """
        Tests that the wide moves are the three turns of every face off the axes of the target and the
        source, at the cell's depth.

        :param cell: The cell of the middle line
        :param target: The face the center is built on
        :param source: The face the piece is on, or None for the target itself
        :param expected_faces: The faces the wide moves are made from
        :return: None
        """

        # Build the wide moves
        moves = wide_moves(5, cell, target, source)

        # Assert
        assert {move[0] for move in moves} == expected_faces
        assert len(moves) == 3 * len(expected_faces)
        assert all(move[1] == "w" for move in moves)


class TestLineRoutes:
    def test_success(self) -> None:
        """
        Tests that there is a bare route and three restoring ones - one per lift - for every turn of
        the target, turn of the source and wide move, the bare ones first.

        :return: None
        """

        # Build the routes
        routes = line_routes(5, (2, 1), CenterSearchResult(Layer.FRONT, 1, 2), Layer.RIGHT)

        # Assert
        assert len(routes) == 4 * 4 * 6 * 4 == len(set(routes))
        assert routes[:2] == ["Uw", "Uw'"]
        assert routes[96] == "Uw R Uw' R'"

    # fmt: off
    @pytest.mark.parametrize("source", [Layer.FRONT, Layer.UP, Layer.LEFT, Layer.BACK])
    # fmt: on
    def test_restoring_routes_change_only_target_and_source(self, source: Layer) -> None:
        """
        Tests that every restoring route that brings the piece in changes no center outside the
        target and the source face, and leaves the fixed center of the target in place.

        :param source: The face the piece is on
        :return: None
        """

        # Paint the piece a colour no other face shows, and mark a second cube
        cube = Cube(5)
        cube.layers[Layer.LEFT] = [Color.RED] * 25
        cube.layers[source][1 * 5 + 2] = Color.ORANGE
        marked = _marked_cube(5)
        routes = line_routes(5, (2, 1), CenterSearchResult(source, 1, 2), Layer.RIGHT)
        delivering = [
            route for route in routes[len(routes) // 4 :] if trial(cube, route).layers[Layer.RIGHT][11] is Color.ORANGE
        ]

        # Assert
        assert delivering
        for route in delivering:
            result = trial(marked, route)
            assert set(_changed_centers(marked, result)) <= {Layer.RIGHT, source}
            assert result.layers[Layer.RIGHT][12] is marked.layers[Layer.RIGHT][12]

    # fmt: off
    @pytest.mark.parametrize("source", [Layer.FRONT, Layer.UP, Layer.LEFT, Layer.BACK, Layer.DOWN])
    @pytest.mark.parametrize("cell", [(3, 2), (3, 4), (3, 1), (3, 5)])
    # fmt: on
    def test_delivers_the_piece(self, source: Layer, cell: tuple[int, int]) -> None:
        """
        Tests that a piece painted on any cell of its type on any other face is brought into the cell
        of a 7x7's middle line by a bare route and by a restoring one.

        :param source: The face the piece is on
        :param cell: The cell of the middle line
        :return: None
        """

        for row, col in orbit_cells(7, cell):
            # Paint one piece a colour no face shows
            cube = Cube(7)
            cube.layers[Layer.LEFT] = [Color.RED] * 49
            cube.layers[source][row * 7 + col] = Color.ORANGE
            routes = line_routes(7, cell, CenterSearchResult(source, row, col), Layer.RIGHT)

            # Assert
            filled = [trial(cube, route).layers[Layer.RIGHT][cell[0] * 7 + cell[1]] is Color.ORANGE for route in routes]
            assert any(filled[: len(routes) // 4]) and any(filled[len(routes) // 4 :])


class TestLineTargetRoutes:
    def test_success(self) -> None:
        """
        Tests that every route turns the target, makes a wide move and undoes both, in that order.

        :return: None
        """

        # Build the routes
        routes = line_target_routes(7, (1, 3), Layer.DOWN)

        # Assert
        assert len(routes) == 3 * 12
        assert routes[:2] == ["D Lw D' Lw'", "D Lw' D' Lw"]

    # fmt: off
    @pytest.mark.parametrize("cell", [(3, 2), (3, 4), (3, 1), (3, 5)])
    # fmt: on
    def test_delivers_the_piece(self, cell: tuple[int, int]) -> None:
        """
        Tests that a piece painted on any other cell of the target of the cell's type is moved onto
        the cell of a 7x7's middle line.

        :param cell: The cell of the middle line
        :return: None
        """

        for row, col in orbit_cells(7, cell)[1:]:
            # Paint one piece a colour no face shows
            cube = Cube(7)
            cube.layers[Layer.LEFT] = [Color.RED] * 49
            cube.layers[Layer.RIGHT][row * 7 + col] = Color.ORANGE

            # Assert
            assert any(
                trial(cube, route).layers[Layer.RIGHT][cell[0] * 7 + cell[1]] is Color.ORANGE
                for route in line_target_routes(7, cell, Layer.RIGHT)
            )


class TestLineLiftRoutes:
    def test_success(self) -> None:
        """
        Tests that UP is turned to stand the piece above the cell, and that FRONT is turned both ways
        between the slice and its undo.

        :return: None
        """

        # Assert
        assert line_lift_routes(5, (2, 1), CenterSearchResult(Layer.UP, 1, 2)) == [
            "U' Lw L' F L Lw' F'",
            "U' Lw L' F' L Lw' F",
        ]

    def test_no_turn_of_up(self) -> None:
        """
        Tests that a piece already standing above the cell needs no turn of UP.

        :return: None
        """

        # Assert
        assert line_lift_routes(5, (2, 3), CenterSearchResult(Layer.UP, 2, 3)) == [
            "Rw' R F R' Rw F'",
            "Rw' R F' R' Rw F",
        ]

    # fmt: off
    @pytest.mark.parametrize("cell", [(3, 2), (3, 4), (3, 1), (3, 5)])
    # fmt: on
    def test_delivers_the_piece(self, cell: tuple[int, int]) -> None:
        """
        Tests that a piece painted on any cell of its type on UP is brought into the cell of a 7x7's
        middle row by both routes, with the rest of the middle row in place and no center outside
        FRONT and UP changed.

        :param cell: The cell of the middle row
        :return: None
        """

        marked = _marked_cube(7)
        line = [(3, col) for col in range(1, 6) if (3, col) != cell]

        for row, col in orbit_cells(7, cell):
            # Paint one piece of UP with the colour of BACK, which no route changes
            cube = Cube(7)
            cube.layers[Layer.UP][row * 7 + col] = Color.BLUE

            for route in line_lift_routes(7, cell, CenterSearchResult(Layer.UP, row, col)):
                result = trial(marked, route)

                # Assert
                assert trial(cube, route).layers[Layer.FRONT][cell[0] * 7 + cell[1]] is Color.BLUE
                assert set(_changed_centers(marked, result)) <= {Layer.FRONT, Layer.UP}
                assert all(
                    result.layers[Layer.FRONT][r * 7 + c] is marked.layers[Layer.FRONT][r * 7 + c] for r, c in line
                )


class TestStagingMiddleRoutes:
    # fmt: off
    @pytest.mark.parametrize(
        "size, cell, piece, expected", [
            (5, (3, 2), CenterSearchResult(Layer.UP, 1, 2),    ["U2"]),
            (5, (3, 2), CenterSearchResult(Layer.FRONT, 2, 1), ["Lw' U' Lw"]),
            (5, (3, 2), CenterSearchResult(Layer.FRONT, 2, 3), ["Rw U Rw'"]),
            (7, (5, 3), CenterSearchResult(Layer.FRONT, 3, 1), ["Lw' U' Lw"]),
            (7, (4, 3), CenterSearchResult(Layer.FRONT, 3, 4), ["3Rw U 3Rw'"]),
        ]
    )
    # fmt: on
    def test_success(self, size: int, cell: tuple[int, int], piece: CenterSearchResult, expected: list[str]) -> None:
        """
        Tests that a piece on UP only needs UP turned, and that a piece on FRONT is raised by the
        block from its nearer side, as deep as its column.

        :param size: The cube size
        :param cell: The middle cell of the staging row
        :param piece: The piece
        :param expected: The routes
        :return: None
        """

        # Assert
        assert staging_middle_routes(size, cell, piece) == expected

    # fmt: off
    @pytest.mark.parametrize("cell, col", [((4, 3), 2), ((4, 3), 4), ((5, 3), 1), ((5, 3), 5)])
    # fmt: on
    def test_raises_a_front_piece(self, cell: tuple[int, int], col: int) -> None:
        """
        Tests that a piece painted in the middle row of a 7x7's FRONT lands on the middle cell of the
        staging row, and that FRONT's middle column and every center outside FRONT and UP stay put.

        :param cell: The middle cell of the staging row
        :param col: The column of FRONT the piece is in
        :return: None
        """

        # Paint the piece with the colour of BACK, which no route changes
        cube = Cube(7)
        cube.layers[Layer.FRONT][3 * 7 + col] = Color.BLUE
        marked = _marked_cube(7)
        route = staging_middle_routes(7, cell, CenterSearchResult(Layer.FRONT, 3, col))[0]
        result = trial(marked, route)

        # Assert
        assert trial(cube, route).layers[Layer.UP][cell[0] * 7 + cell[1]] is Color.BLUE
        assert set(_changed_centers(marked, result)) <= {Layer.FRONT, Layer.UP}
        assert all(
            result.layers[Layer.FRONT][row * 7 + 3] is marked.layers[Layer.FRONT][row * 7 + 3] for row in range(1, 6)
        )


class TestCommutatorRoutes:
    def test_success(self) -> None:
        """
        Tests that the upward slice of every column holding the target's position type is paired with
        every turn of UP in both orders, and that the conjugated forms follow the plain ones.

        :return: None
        """

        # Build the routes
        routes = commutator_routes(7, (4, 2))

        # Assert
        assert len(routes) == 2 * 3 * 2 * 4 == len(set(routes))
        assert routes[:2] == ["3Lw' Lw U Lw' 3Lw U'", "U 3Lw' Lw U' Lw' 3Lw"]
        assert routes[12] == "U 3Lw' Lw U Lw' 3Lw U' U'"

    def test_middle_column_left_out(self) -> None:
        """
        Tests that the middle column of an odd cube, which carries the fixed centers, is never
        sliced, even when a cell of the position type lies in it.

        :return: None
        """

        # Build the routes: the position type of (3, 2) on a 5x5 lies in columns 1, 2 and 3
        routes = commutator_routes(5, (3, 2))

        # Assert
        assert len(routes) == 2 * 3 * 2 * 4
        assert not any("x" in route for route in routes)

    # fmt: off
    @pytest.mark.parametrize("size, cell", [(4, (2, 1)), (6, (3, 2)), (7, (5, 1))])
    # fmt: on
    def test_changes_only_front_and_up(self, size: int, cell: tuple[int, int]) -> None:
        """
        Tests that no route changes a center outside FRONT and UP.

        :param size: The cube size
        :param cell: The cell of the staging row
        :return: None
        """

        marked = _marked_cube(size)

        # Assert
        for route in commutator_routes(size, cell):
            assert set(_changed_centers(marked, trial(marked, route))) <= {Layer.FRONT, Layer.UP}


class TestFrontInsertion:
    # fmt: off
    @pytest.mark.parametrize(
        "size, col, expected", [
            (4, 1, "U Lw F2 Lw' F2"),
            (7, 2, "U 3Lw F2 3Lw' F2"),
            (7, 1, "U Lw F2 Lw' F2"),
            (8, 3, "U 4Lw F2 4Lw' F2"),
        ]
    )
    # fmt: on
    def test_success(self, size: int, col: int, expected: str) -> None:
        """
        Tests that the block from LEFT reaches as far as the column.

        :param size: The cube size
        :param col: The column of FRONT
        :param expected: The algorithm
        :return: None
        """

        # Assert
        assert front_insertion(size, col) == expected

    # fmt: off
    @pytest.mark.parametrize("size, col", [(4, 1), (6, 2), (6, 1), (7, 2), (7, 1)])
    # fmt: on
    def test_bar_lands_in_its_column(self, size: int, col: int) -> None:
        """
        Tests that a bar painted in its staging row of UP lands in the column of FRONT, that the
        columns of FRONT between it and its mirror stay put, and that no center outside FRONT and UP
        changes.

        :param size: The cube size
        :param col: The column of FRONT
        :return: None
        """

        # Paint the bar with the colour of BACK, which the insertion never changes
        cube = Cube(size)
        for index in range(1, size - 1):
            cube.layers[Layer.UP][(size - 1 - col) * size + index] = Color.BLUE
        marked = _marked_cube(size)
        landed = trial(cube, front_insertion(size, col))
        result = trial(marked, front_insertion(size, col))
        kept = [(row, index) for row in range(1, size - 1) for index in range(col + 1, size - 1 - col)]

        # Assert
        assert all(landed.layers[Layer.FRONT][row * size + col] is Color.BLUE for row in range(1, size - 1))
        assert all(
            result.layers[Layer.FRONT][r * size + c] is marked.layers[Layer.FRONT][r * size + c] for r, c in kept
        )
        assert set(_changed_centers(marked, result)) <= {Layer.FRONT, Layer.UP}


class TestCycleRoutes:
    def test_success(self) -> None:
        """
        Tests the commutator for a cell whose quarter turn one way keeps it in its column: only the
        other way is used.

        :return: None
        """

        # Assert
        assert cycle_routes(7, (2, 4), CenterSearchResult(Layer.UP, 2, 4)) == [
            "3Rw' Rw F' 3Lw Lw' F Rw' 3Rw F' Lw 3Lw' F"
        ]

    def test_both_turns(self) -> None:
        """
        Tests that a cell off the diagonals gets a route for each quarter turn, with UP turned first.

        :return: None
        """

        # Assert
        assert cycle_routes(6, (1, 3), CenterSearchResult(Layer.UP, 3, 4)) == [
            "U' 3Rw' Rw F Rw' R F' Rw' 3Rw F R' Rw F'",
            "U' 3Rw' Rw F' Lw L' F Rw' 3Rw F' L Lw' F",
        ]

    # fmt: off
    @pytest.mark.parametrize("size", [4, 5, 6, 7])
    # fmt: on
    def test_changes_only_the_cell(self, size: int) -> None:
        """
        Tests that for every cell of FRONT's right half and every piece of its type on UP, each route
        brings the piece in, and changes no other cell of FRONT and no center outside FRONT and UP.

        :param size: The cube size
        :return: None
        """

        marked = _marked_cube(size)
        columns = [col for col in range(1, size - 1) if 2 * col > size - 1]

        for cell in [(row, col) for col in columns for row in range(1, size - 1)]:
            for row, col in orbit_cells(size, cell):
                # Paint one piece of UP with the colour of BACK, which no route changes
                cube = Cube(size)
                cube.layers[Layer.UP][row * size + col] = Color.BLUE

                for route in cycle_routes(size, cell, CenterSearchResult(Layer.UP, row, col)):
                    changed = _changed_centers(marked, trial(marked, route))

                    # Assert
                    assert trial(cube, route).layers[Layer.FRONT][cell[0] * size + cell[1]] is Color.BLUE
                    assert set(changed) <= {Layer.FRONT, Layer.UP}
                    assert changed.get(Layer.FRONT, set()) <= {cell}
