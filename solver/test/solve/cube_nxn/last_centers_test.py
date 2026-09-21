# Python imports
import random
from typing import Callable

import pytest

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.scramble.scrambler import Scrambler
from rubik_cube_solver.solve.center_search import search_center
from rubik_cube_solver.solve.cube_nxn import last_centers
from rubik_cube_solver.solve.cube_nxn.centers import build_first_four_centers
from rubik_cube_solver.solve.cube_nxn.last_centers import (
    build_front_bar,
    build_front_line,
    build_last_two_centers,
    fill_right_half,
    fill_staging_cell,
)
from rubik_cube_solver.solve.cube_nxn.pieces import CenterSticker, fixed_centers
from rubik_cube_solver.solve.cube_nxn.routes import inverse_of, line_lift_routes, staging_middle_routes, trial

# The whole-cube rotation that turns a solved cube into the grip the first four centers end in: blue
# on FRONT, orange on UP, yellow on RIGHT, white on LEFT, green on BACK and red on DOWN.
LAST_TWO_GRIP: str = "y2 z'"

# The face every center ends on in that grip.
# fmt: off
CENTER_FACES: dict[Color, Layer] = {
    Color.BLUE:   Layer.FRONT,
    Color.ORANGE: Layer.UP,
    Color.YELLOW: Layer.RIGHT,
    Color.WHITE:  Layer.LEFT,
    Color.GREEN:  Layer.BACK,
    Color.RED:    Layer.DOWN,
}
# fmt: on

# The algorithms the user gives for a 7x7's first bar, one per cell the piece for UP (4, 2) - the cell
# left of the bar's middle piece - can start from.
# fmt: off
STAGING_CASES: list[tuple[Layer, int, int, str]] = [
    (Layer.UP,    4, 4, "3Rw Rw' U2 3Rw' Rw U' 3Rw Rw' U 3Rw' Rw U2"),
    (Layer.UP,    2, 4, "3Rw Rw' U2 3Rw' Rw U2"),
    (Layer.UP,    2, 2, "U 3Rw Rw' U 3Rw' Rw U2"),
    (Layer.FRONT, 2, 2, "3Lw' Lw U' 3Lw Lw' U 3Lw' Lw U' 3Lw Lw' U"),
    (Layer.FRONT, 2, 4, "U2 3Rw Rw' U2 3Rw' Rw"),
    (Layer.FRONT, 4, 2, "3Lw' Lw U' 3Lw Lw' U"),
    (Layer.FRONT, 4, 4, "U' 3Rw Rw' U' 3Rw' Rw U' 3Rw Rw' U2 3Rw' Rw"),
]
# fmt: on


def _center_is(cube: Cube, face: Layer, color: Color) -> bool:
    """
    Checks whether every center cell of a face holds a colour, by reading raw stickers.

    :param cube: The cube
    :param face: The face
    :param color: The colour
    :return: Whether the whole center of the face is that colour
    """

    size = cube.size

    return all(cube.layers[face][row * size + col] is color for row in range(1, size - 1) for col in range(1, size - 1))


def _stickers(cube: Cube, face: Layer, cells: list[tuple[int, int]]) -> list[CenterSticker]:
    """
    Returns cells of a face, each tagged with the colour it holds now.

    :param cube: The cube
    :param face: The face
    :param cells: The cells
    :return: The cells with their colours
    """

    return [CenterSticker(face, row, col, cube.layers[face][row * cube.size + col]) for row, col in cells]


class TestBuildFrontLine:
    def test_success(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that a cell of the middle row whose piece was carried up to UP is filled from there.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(5, "Lw' L U")

        # Build the line
        moves, result = build_front_line(cube, Color.GREEN, [])

        # Assert
        assert moves == ["U' Lw L' F L Lw' F'"]
        assert all(result.layers[Layer.FRONT][2 * 5 + col] is Color.GREEN for col in (1, 3))

    def test_already_filled(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that a middle row already in the colour needs no moves.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube: FRONT is green
        cube = generate_cube(5, "")

        # Assert
        assert build_front_line(cube, Color.GREEN, []) == ([], cube)

    def test_keeps_what_is_protected(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that on a 7x7 whose middle row was scattered over UP every cell is filled, and that the
        fixed centers kept stay where they were.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(7, "Lw' L U 3Lw' Lw U2 Rw' R U' 3Rw' Rw")

        # Build the line
        _, result = build_front_line(cube, Color.GREEN, fixed_centers(cube))

        # Assert
        assert all(result.layers[Layer.FRONT][3 * 7 + col] is Color.GREEN for col in range(1, 6))
        assert fixed_centers(result) == fixed_centers(cube)

    def test_next_piece_tried(self, generate_cube: Callable[[int, str], Cube], monkeypatch: pytest.MonkeyPatch) -> None:
        """
        Tests that when no route brings in the first piece on UP, the next piece on UP is tried.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param monkeypatch: Fixture giving the first piece on UP no routes
        :return: None
        """

        # Generate the cube: the slices carry both side columns of FRONT up to UP
        cube = generate_cube(5, "Lw' L Rw R'")
        first, second = [piece for piece in search_center(cube, Color.GREEN, 2, 1) if piece.layer is Layer.UP]
        monkeypatch.setattr(
            last_centers,
            "line_lift_routes",
            lambda size, cell, piece: [] if piece == first else line_lift_routes(size, cell, piece),
        )

        # Build the line
        moves, result = build_front_line(cube, Color.GREEN, [])

        # Assert
        assert moves[0] in line_lift_routes(5, (2, 1), second)
        assert all(result.layers[Layer.FRONT][2 * 5 + col] is Color.GREEN for col in (1, 3))

    def test_invalid_no_route(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that a cell no route can fill raises a ValueError naming the cell and the colour.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube: the half turn of the slice carries the piece to BACK, so none is on UP
        cube = generate_cube(5, "Lw2 L2")

        # Assert
        with pytest.raises(ValueError, match=r"No route fills FRONT \(2, 1\) of the GREEN middle line"):
            build_front_line(cube, Color.GREEN, [])


class TestFillStagingCell:
    def test_success(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that a commutator brings a piece into the cell.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(5, "Rw R' U2 R Rw' U2")

        # Fill the cell
        route, result = fill_staging_cell(cube, Color.WHITE, (3, 1), [])

        # Assert
        assert route == "Lw' L U L' Lw U'"
        assert result.layers[Layer.UP][3 * 5 + 1] is Color.WHITE

    # fmt: off
    @pytest.mark.parametrize("face, row, col, algorithm", STAGING_CASES)
    # fmt: on
    def test_dictated_cases(self, face: Layer, row: int, col: int, algorithm: str) -> None:
        """
        Tests every case of a 7x7's first bar the user solves by hand: the piece for the cell left of
        the bar's middle piece is set up in its starting cell by undoing the user's algorithm, and
        is brought in with the middle piece and the middle line kept.

        :param face: The face the piece starts on
        :param row: The row it starts in
        :param col: The column it starts in
        :param algorithm: The user's algorithm for the case
        :return: None
        """

        # Paint every sticker orange but the piece, the middle piece and the middle line
        layers = {layer: [Color.ORANGE] * 49 for layer in Layer}
        layers[Layer.UP][4 * 7 + 2] = Color.BLUE
        layers[Layer.UP][4 * 7 + 3] = Color.RED
        for line_row in range(1, 6):
            layers[Layer.FRONT][line_row * 7 + 3] = Color.GREEN
        cube = trial(Cube(7, layers), inverse_of(algorithm))
        protect = [CenterSticker(Layer.UP, 4, 3, Color.RED)]
        protect += [CenterSticker(Layer.FRONT, line_row, 3, Color.GREEN) for line_row in range(1, 6)]

        # Fill the cell
        _, result = fill_staging_cell(cube, Color.BLUE, (4, 2), protect)

        # Assert
        assert cube.layers[face][row * 7 + col] is Color.BLUE
        assert result.layers[Layer.UP][4 * 7 + 2] is Color.BLUE
        assert all(result.layers[kept.layer][kept.row * 7 + kept.col] is kept.color for kept in protect)

    def test_two_commutators(self, generate_cube: Callable[[int, str], Cube], monkeypatch: pytest.MonkeyPatch) -> None:
        """
        Tests that when no single commutator fills the cell, a first step that keeps everything
        protected is followed by one that fills it, and that a first step breaking a protected cell
        is skipped.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param monkeypatch: Fixture replacing the commutators with a list of three routes
        :return: None
        """

        # Generate the cube: `Rw R'` fills the cell but breaks the kept FRONT cell, `Lw' L` brings green
        # into UP's left column, and `U` then turns it into the cell
        cube = generate_cube(4, "")
        monkeypatch.setattr(last_centers, "commutator_routes", lambda size, cell: ["Rw R'", "Lw' L", "U"])

        # Fill the cell
        route, result = fill_staging_cell(cube, Color.GREEN, (1, 2), [CenterSticker(Layer.FRONT, 1, 2, Color.GREEN)])

        # Assert
        assert route == "Lw' L U"
        assert result.layers[Layer.UP][1 * 4 + 2] is Color.GREEN

    def test_invalid_no_route(self, generate_cube: Callable[[int, str], Cube], monkeypatch: pytest.MonkeyPatch) -> None:
        """
        Tests that a cell no commutator or pair of them can fill raises a ValueError naming the cell
        and the colour.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param monkeypatch: Fixture replacing the commutators with a turn of UP alone
        :return: None
        """

        # Generate the cube: no green piece is on UP, and turning UP brings none
        cube = generate_cube(4, "")
        monkeypatch.setattr(last_centers, "commutator_routes", lambda size, cell: ["U"])

        # Assert
        with pytest.raises(ValueError, match=r"No route fills UP \(1, 2\) of the GREEN bar"):
            fill_staging_cell(cube, Color.GREEN, (1, 2), [])


class TestBuildFrontBar:
    def test_success(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that the bar is staged cell by cell and inserted into its column of FRONT.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(4, "Lw' L U2")

        # Build the bar
        moves, result = build_front_bar(cube, Color.GREEN, 1, [], [])

        # Assert
        assert moves == ["U Lw' L U' L' Lw", "Rw R' U R Rw' U'", "U Lw F2 Lw' F2"]
        assert all(result.layers[Layer.FRONT][row * 4 + 1] is Color.GREEN for row in (1, 2))

    def test_staged_cell_already_filled(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that a staged cell already in the colour is left as it is.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube: `Lw' L` carries green into UP (2, 1)
        cube = generate_cube(4, "Lw' L")

        # Build the bar
        moves, result = build_front_bar(cube, Color.GREEN, 1, [], [])

        # Assert
        assert len(moves) == 2
        assert moves[-1] == "U Lw F2 Lw' F2"
        assert all(result.layers[Layer.FRONT][row * 4 + 1] is Color.GREEN for row in (1, 2))

    def test_middle_piece_from_front(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that on an odd cube the bar's middle piece comes first, raised from a free cell of FRONT
        when UP holds none, and that the middle line stays put.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube: FRONT is green and its middle column holds the middle line
        cube = generate_cube(5, "")

        # Build the bar
        moves, result = build_front_bar(cube, Color.GREEN, 1, [(1, 2), (3, 2)], [])

        # Assert
        assert moves[0] == "Lw' U' Lw"
        assert all(result.layers[Layer.FRONT][row * 5 + col] is Color.GREEN for row in (1, 2, 3) for col in (1, 2))

    def test_middle_piece_from_up(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that the bar's middle piece is brought in by a turn of UP when one is there.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube: `Rw R'` carries FRONT's right column, with a piece of the type, up to UP
        cube = generate_cube(5, "Rw R'")

        # Build the bar
        moves, result = build_front_bar(cube, Color.GREEN, 1, [(1, 2), (3, 2)], [])

        # Assert
        assert moves[0] == "U"
        assert all(result.layers[Layer.FRONT][row * 5 + 1] is Color.GREEN for row in (1, 2, 3))

    def test_next_middle_piece_tried(
        self, generate_cube: Callable[[int, str], Cube], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """
        Tests that when the piece on UP cannot be brought to the middle cell, a piece on FRONT is
        tried next.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param monkeypatch: Fixture giving the pieces on UP no routes
        :return: None
        """

        # Generate the cube: `Rw R'` carries a piece of the type up to UP, and another stays on FRONT
        cube = generate_cube(5, "Rw R'")
        monkeypatch.setattr(
            last_centers,
            "staging_middle_routes",
            lambda size, cell, piece: [] if piece.layer is Layer.UP else staging_middle_routes(size, cell, piece),
        )

        # Build the bar
        moves, _ = build_front_bar(cube, Color.GREEN, 1, [(1, 2), (3, 2)], [])

        # Assert
        assert moves[0] == "Lw' U' Lw"

    def test_invalid_no_middle_piece(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that a middle cell with no free piece to fill it raises a ValueError naming the cell and
        the colour.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube: every green piece of the type is on FRONT, in cells already built
        cube = generate_cube(5, "")

        # Assert
        with pytest.raises(ValueError, match=r"No route fills UP \(3, 2\) of the GREEN bar"):
            build_front_bar(cube, Color.GREEN, 1, [(1, 2), (2, 1), (2, 3), (3, 2)], [])


class TestFillRightHalf:
    def test_success(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that each cell of FRONT's right half is brought back down from UP on its own.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(4, "Rw R'")

        # Fill the right half
        moves, result = fill_right_half(cube, Color.GREEN, [(1, 1), (2, 1)], [])

        # Assert
        assert moves == ["Rw' R F' Lw L' F R' Rw F' L Lw' F", "Rw' R F Lw L' F' R' Rw F L Lw' F'"]
        assert _center_is(result, Layer.FRONT, Color.GREEN)

    def test_already_filled(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that a right half already in the colour needs no moves.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube: FRONT is green
        cube = generate_cube(4, "")

        # Assert
        assert fill_right_half(cube, Color.GREEN, [(1, 1), (2, 1)], []) == ([], cube)

    def test_invalid_no_route(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that a cell no route can fill raises a ValueError naming the cell and the colour.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube: the pieces are on UP, but every cell of UP is kept as it is
        cube = generate_cube(4, "Rw R'")
        keep = _stickers(cube, Layer.UP, [(row, col) for row in (1, 2) for col in (1, 2)])

        # Assert
        with pytest.raises(ValueError, match=r"No route fills FRONT \(1, 2\) of the GREEN center"):
            fill_right_half(cube, Color.GREEN, [(1, 1), (2, 1)], keep)


class TestBuildLastTwoCenters:
    def test_success(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that the returned algorithms, applied to the cube, build blue on FRONT and orange on UP
        with the other four centers kept, and that the cube itself is not turned.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(4, f"{LAST_TWO_GRIP} Lw' L U L' Lw")

        # Build the centers
        moves = build_last_two_centers(cube)
        result = trial(cube, " ".join(moves))

        # Assert
        assert moves == [
            "U2 Lw' L U2 L' Lw",
            "U Lw F2 Lw' F2",
            "U Rw' R F' Lw L' F R' Rw F' L Lw' F",
            "U Rw' R F Lw L' F' R' Rw F L Lw' F'",
        ]
        assert all(_center_is(result, face, color) for color, face in CENTER_FACES.items())
        assert cube.layers == generate_cube(4, f"{LAST_TWO_GRIP} Lw' L U L' Lw").layers

    def test_odd_cube(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that on an odd cube the middle row of FRONT is built first and turned upright.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(5, f"{LAST_TWO_GRIP} Lw' L U L' Lw")

        # Build the centers
        moves = build_last_two_centers(cube)
        result = trial(cube, " ".join(moves))

        # Assert
        assert moves[:2] == ["U' Lw L' F L Lw' F'", "F"]
        assert all(_center_is(result, face, color) for color, face in CENTER_FACES.items())
        assert fixed_centers(result) == fixed_centers(cube)

    # fmt: off
    @pytest.mark.parametrize("size", [4, 5, 6, 7])
    # fmt: on
    def test_random_scrambles(self, generate_cube: Callable[[int, str], Cube], size: int) -> None:
        """
        Tests that all six centers are built from seeded random scrambles, once the first four are.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param size: The cube size
        :return: None
        """

        random.seed(size)

        for _ in range(3):
            # Scramble the cube and build the first four centers
            scramble = str(Algorithm(Scrambler().generate_scramble(size)))
            cube = generate_cube(size, scramble)
            cube = trial(cube, " ".join(build_first_four_centers(cube)))

            # Build the last two
            result = trial(cube, " ".join(build_last_two_centers(cube)))

            # Assert
            assert all(_center_is(result, face, color) for color, face in CENTER_FACES.items()), scramble
