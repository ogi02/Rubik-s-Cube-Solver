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
    direct_route,
    extraction,
    insertion,
    inverse_of,
    lift,
    quarter_direction,
    staging_routes,
    target_routes,
    trial,
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


class TestColumnSlice:
    # fmt: off
    @pytest.mark.parametrize(
        "col, direction, expected", [
            (1, Direction.CW,     "Lw' L"),
            (2, Direction.CW,     "3Lw' Lw"),
            (3, Direction.CW,     "3Rw Rw'"),
            (4, Direction.CW,     "Rw R'"),
            (1, Direction.DOUBLE, "Lw2 L2"),
            (4, Direction.CCW,    "Rw' R"),
        ]
    )
    # fmt: on
    def test_success(self, col: int, direction: Direction, expected: str) -> None:
        """
        Tests that the layer is reached from the nearer side, as the block ending at it followed by
        the block in front of it turned back, with the direction inverted from LEFT.

        :param col: The column of FRONT
        :param direction: The direction, as seen from RIGHT
        :param expected: The turn
        :return: None
        """

        # Assert
        assert column_slice(6, col, direction) == expected

    # fmt: off
    @pytest.mark.parametrize("col", [1, 2, 3, 4])
    # fmt: on
    def test_moves_only_its_column(self, col: int) -> None:
        """
        Tests that of FRONT only the column itself moves, and that the centers of LEFT and RIGHT do
        not move at all.

        :param col: The column of FRONT
        :return: None
        """

        # Mark the cube and turn the slice
        cube = _marked_cube(6)
        changed = _changed_centers(cube, trial(cube, column_slice(6, col, Direction.CW)))

        # Assert
        assert changed[Layer.FRONT] == {(row, col) for row in range(1, 5)}
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
        "side, row, expected", [
            (Layer.LEFT,  1, "Uw B2 Uw'"),
            (Layer.RIGHT, 1, "Uw' B2 Uw"),
            (Layer.RIGHT, 3, "3Dw B2 3Dw'"),
            (Layer.LEFT,  4, "Dw' B2 Dw"),
        ]
    )
    # fmt: on
    def test_success(self, side: Layer, row: int, expected: str) -> None:
        """
        Tests that the block reaches in from the nearer pole, as deep as the piece's row, and turns
        towards BACK.

        :param side: The face the piece is on
        :param row: The row of the piece
        :param expected: The conjugate
        :return: None
        """

        # Assert
        assert extraction(6, side, row) == expected

    # fmt: off
    @pytest.mark.parametrize("side", [Layer.LEFT, Layer.RIGHT])
    @pytest.mark.parametrize("row", [1, 2, 3, 4])
    # fmt: on
    def test_moves_the_piece_to_back(self, side: Layer, row: int) -> None:
        """
        Tests that a piece painted on the side face ends on BACK, and that no center outside BACK and
        that side face moves.

        :param side: The face the piece is on
        :param row: The row of the piece
        :return: None
        """

        # Paint one piece of the side face with the colour of UP, which the conjugate never changes
        cube = Cube(6)
        cube.layers[side][row * 6 + 1] = Color.WHITE
        marked = _marked_cube(6)

        # Assert
        parked = trial(cube, extraction(6, side, row))
        assert any(piece.layer is Layer.BACK for piece in search_center(parked, Color.WHITE, row, 1))
        assert set(_changed_centers(marked, trial(marked, extraction(6, side, row)))) <= {Layer.BACK, side}


class TestAcrossRoutes:
    def test_success(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that there is one bare route per piece of the colour on BACK after the extraction, and
        that each of them fills the cell.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(4, "z' Dw")

        # Build the routes
        routes = across_routes(cube, Color.YELLOW, (2, 1), CenterSearchResult(Layer.RIGHT, 1, 1))

        # Assert
        assert routes == ["Uw' B2 Uw B2 Lw2 L2", "Uw' B2 Uw B' Lw2 L2"]
        assert all(trial(cube, route).layers[Layer.FRONT][2 * 4 + 1] is Color.YELLOW for route in routes)


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
        assert lift(6, col) == expected

    # fmt: off
    @pytest.mark.parametrize("col", [1, 2, 3, 4])
    # fmt: on
    def test_moves_the_piece_to_up(self, col: int) -> None:
        """
        Tests that a piece painted on DOWN ends on UP, and that no center outside UP and DOWN moves.

        :param col: The column of DOWN
        :return: None
        """

        # Paint one piece of DOWN with the colour of BACK, which the conjugate never changes
        cube = Cube(6)
        cube.layers[Layer.DOWN][2 * 6 + col] = Color.BLUE
        marked = _marked_cube(6)

        # Assert
        lifted = trial(cube, lift(6, col))
        assert any(piece.layer is Layer.UP for piece in search_center(lifted, Color.BLUE, 2, col))
        assert set(_changed_centers(marked, trial(marked, lift(6, col)))) <= {Layer.UP, Layer.DOWN}


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
        up_pieces = search_center(trial(cube, lift(4, 1)), Color.YELLOW, 2, 1)

        # Assert
        assert len(routes) == 2 * sum(1 for piece in up_pieces if piece.layer is Layer.UP)
        assert all(route.startswith("Lw2 U2 Lw2 ") for route in routes)
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
