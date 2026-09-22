# Python imports
import random
from typing import Callable

import pytest

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.Direction import Direction
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.scramble.scrambler import Scrambler
from rubik_cube_solver.solve.center_search import CenterSearchResult
from rubik_cube_solver.solve.cube_nxn import centers
from rubik_cube_solver.solve.cube_nxn.centers import (
    CENTERS_PLAN,
    build_bar,
    build_center,
    build_first_four_centers,
    build_middle_line,
    fetch,
    fetch_line_piece,
    first_route,
)
from rubik_cube_solver.solve.cube_nxn.pieces import Sticker, fixed_centers
from rubik_cube_solver.solve.cube_nxn.routes import lift, line_target_routes, staging_routes, trial

YELLOW_PRIORITY: tuple[tuple[Layer, ...], ...] = CENTERS_PLAN[0].priority

# The face each of the first four centers ends on once they are built, starting from the standard
# grip: the regrips `z'`, `x'` and `x'` leave yellow on RIGHT, white on LEFT, green on BACK and red
# on DOWN.
# fmt: off
FIRST_FOUR_FACES: dict[Color, Layer] = {
    Color.YELLOW: Layer.RIGHT,
    Color.WHITE:  Layer.LEFT,
    Color.GREEN:  Layer.BACK,
    Color.RED:    Layer.DOWN,
}
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


class TestFetch:
    def test_success(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that a piece on a column-slice face is brought in straight, and that the returned cube
        is the given one with the returned route applied.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube: yellow's lower half is on BACK
        cube = generate_cube(4, "z' Dw")

        # Fetch
        route, result = fetch(cube, Color.YELLOW, (2, 1), CenterSearchResult(Layer.BACK, 2, 1), Layer.RIGHT, [])

        # Assert
        assert route == "B2 Lw2 L2"
        assert result.layers == trial(cube, route).layers
        assert result.layers[Layer.FRONT][2 * 4 + 1] is Color.YELLOW

    # fmt: off
    @pytest.mark.parametrize(
        "algorithm, color, piece, target, opening", [
            # A side face is extracted onto BACK first
            ("z' Dw", Color.YELLOW, CenterSearchResult(Layer.RIGHT, 1, 1), Layer.RIGHT, "Uw' B2 Uw "),
            # DOWN is lifted onto UP first while the center is built on DOWN
            ("",      Color.YELLOW, CenterSearchResult(Layer.DOWN, 1, 1),  Layer.DOWN,  "Lw2 U2 Lw2 "),
        ]
    )
    # fmt: on
    def test_conjugate_first(
        self,
        generate_cube: Callable[[int, str], Cube],
        algorithm: str,
        color: Color,
        piece: CenterSearchResult,
        target: Layer,
        opening: str,
    ) -> None:
        """
        Tests that a piece off the column slice is moved onto it by a conjugate before it is brought
        in, and that it arrives.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param algorithm: The algorithm applied to a solved 4x4
        :param color: The colour being built
        :param piece: The piece to bring in
        :param target: The face the center is built on
        :param opening: The conjugate the route has to open with
        :return: None
        """

        # Generate the cube
        cube = generate_cube(4, algorithm)

        # Fetch
        route, result = fetch(cube, color, (2, 1), piece, target, [])

        # Assert
        assert route.startswith(opening)
        assert result.layers[Layer.FRONT][2 * 4 + 1] is color

    def test_front_piece(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that a piece already on FRONT is moved by one of the staging routes.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube: column 1 of FRONT is carried off, the rest of FRONT stays green
        cube = generate_cube(4, "Lw L'")

        # Fetch
        route, result = fetch(cube, Color.GREEN, (2, 1), CenterSearchResult(Layer.FRONT, 2, 2), Layer.RIGHT, [])

        # Assert
        assert route in staging_routes(4)
        assert result.layers[Layer.FRONT][2 * 4 + 1] is Color.GREEN

    def test_no_route(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that None is returned when every route breaks a protected cell.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube and protect the cell being filled with a colour it can never hold
        cube = generate_cube(4, "z' Dw")
        protect = [Sticker(Layer.FRONT, 2, 1, Color.GREEN)]

        # Assert
        assert fetch(cube, Color.YELLOW, (2, 1), CenterSearchResult(Layer.BACK, 2, 1), Layer.RIGHT, protect) is None


class TestFirstRoute:
    def test_success(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that routes that leave the goal cell empty or break a protected cell are passed over, and
        that the cube returned is the given one with the route applied.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube: column 1 of FRONT is carried off
        cube = generate_cube(4, "Lw L'")
        goal = Sticker(Layer.FRONT, 2, 1, Color.GREEN)
        protect = [Sticker(Layer.FRONT, 1, 2, Color.GREEN)]

        # Take the first surviving route
        route, result = first_route(cube, ["U", "F2", "Lw' L"], goal, protect)

        # Assert
        assert route == "Lw' L"
        assert result.layers == trial(cube, route).layers

    def test_no_route(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that None is returned when no route fills the goal cell.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(4, "Lw L'")

        # Assert
        assert first_route(cube, ["U", "D"], Sticker(Layer.FRONT, 2, 1, Color.GREEN), []) is None


class TestFetchLinePiece:
    def test_success(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that a piece on another face is carried into the cell of the middle line, and that the
        returned cube is the given one with the returned route applied.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube: yellow is on RIGHT, and the left cell of its middle line is turned away on DOWN
        cube = generate_cube(5, "z' Fw D")

        # Fetch
        route, result = fetch_line_piece(
            cube, Color.YELLOW, (2, 1), CenterSearchResult(Layer.DOWN, 2, 3), Layer.RIGHT, []
        )

        # Assert
        assert route == "D' Fw'"
        assert result.layers == trial(cube, route).layers
        assert result.layers[Layer.RIGHT][2 * 5 + 1] is Color.YELLOW

    def test_piece_on_target(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that a piece already on the target is moved within it onto the cell of the middle line.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube: yellow is on RIGHT, and the left cell of its middle line is painted over
        cube = generate_cube(5, "z'")
        cube.layers[Layer.RIGHT][2 * 5 + 1] = Color.WHITE

        # Fetch
        route, result = fetch_line_piece(
            cube, Color.YELLOW, (2, 1), CenterSearchResult(Layer.RIGHT, 1, 2), Layer.RIGHT, []
        )

        # Assert
        assert route in line_target_routes(5, (2, 1), Layer.RIGHT)
        assert result.layers[Layer.RIGHT][2 * 5 + 1] is Color.YELLOW

    def test_no_route(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that None is returned when every route breaks a protected cell.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube and protect the cell being filled with a colour it can never hold
        cube = generate_cube(5, "z' Fw D")
        protect = [Sticker(Layer.RIGHT, 2, 1, Color.GREEN)]
        piece = CenterSearchResult(Layer.DOWN, 2, 3)

        # Assert
        assert fetch_line_piece(cube, Color.YELLOW, (2, 1), piece, Layer.RIGHT, protect) is None


class TestBuildMiddleLine:
    # fmt: off
    @pytest.mark.parametrize(
        "algorithm, color, target, vertical", [
            ("z' Uw R Fw' D Bw2 L", Color.YELLOW, Layer.RIGHT, False),
            ("x' Rw U Lw' B Fw2 D", Color.GREEN,  Layer.DOWN,  True),
        ]
    )
    # fmt: on
    def test_success(
        self, generate_cube: Callable[[int, str], Cube], algorithm: str, color: Color, target: Layer, vertical: bool
    ) -> None:
        """
        Tests that every cell of the line ends up in the colour, across the face or down it, and that
        the fixed centers kept are where they were.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param algorithm: The algorithm applied to a solved 7x7
        :param color: The colour being built
        :param target: The face the center is built on
        :param vertical: Whether the line runs down the face
        :return: None
        """

        # Generate the cube
        cube = generate_cube(7, algorithm)

        # Build the line
        _, result = build_middle_line(cube, color, target, vertical, fixed_centers(cube))
        line = [(3, col) for col in (1, 2, 4, 5)] if not vertical else [(row, 3) for row in (1, 2, 4, 5)]

        # Assert
        assert all(result.layers[target][row * 7 + col] is color for row, col in line)
        assert fixed_centers(result) == fixed_centers(cube)

    def test_already_filled(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that a line already in the colour needs no moves.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube: yellow is on RIGHT
        cube = generate_cube(5, "z'")

        # Assert
        assert build_middle_line(cube, Color.YELLOW, Layer.RIGHT, False, []) == ([], cube)

    def test_invalid_no_route(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that a cell no candidate can fill raises a ValueError naming the face, the cell and the
        colour.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube and keep the cell in a colour it can never hold
        cube = generate_cube(5, "z' Fw D")
        keep = [Sticker(Layer.RIGHT, 2, 1, Color.GREEN)]

        # Assert
        with pytest.raises(ValueError, match=r"No route fills RIGHT \(2, 1\) of the YELLOW middle line"):
            build_middle_line(cube, Color.YELLOW, Layer.RIGHT, False, keep)


class TestBuildBar:
    def test_success(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that the bar row ends up in the colour, filled in fill order.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(4, "z' Dw")

        # Build the bar
        moves, result = build_bar(cube, Color.YELLOW, 2, YELLOW_PRIORITY, Layer.RIGHT, [], [])

        # Assert
        assert moves == ["B2 Lw2 L2", "Rw2 R2"]
        assert all(result.layers[Layer.FRONT][2 * 4 + col] is Color.YELLOW for col in (1, 2))

    def test_already_filled(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that a bar row already in the colour needs no moves.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube: FRONT is green
        cube = generate_cube(4, "")

        # Assert
        assert build_bar(cube, Color.GREEN, 2, YELLOW_PRIORITY, Layer.RIGHT, [], []) == ([], cube)

    def test_invalid_no_route(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that a cell no candidate can fill raises a ValueError naming the cell and the colour.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube: yellow is on BACK and RIGHT, and only UP is allowed as a source
        cube = generate_cube(4, "z' Dw")

        # Assert
        with pytest.raises(ValueError, match=r"No route fills FRONT \(2, 1\) of the YELLOW bar"):
            build_bar(cube, Color.YELLOW, 2, ((Layer.UP,),), Layer.RIGHT, [], [])

    def test_front_tried_once(self, generate_cube: Callable[[int, str], Cube], monkeypatch: pytest.MonkeyPatch) -> None:
        """
        Tests that when the only candidates are FRONT pieces, the routes within FRONT are tried for
        the first of them only, since they would be the same routes for the second.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param monkeypatch: Fixture replacing `fetch` with one that counts its calls
        :return: None
        """

        # Generate the cube: two green pieces of the orbit stay on FRONT, and keeping UP, BACK and DOWN
        # as they are rules out every staging route
        cube = generate_cube(4, "Lw L'")
        keep = [
            Sticker(face, row, col, cube.layers[face][row * 4 + col])
            for face in (Layer.UP, Layer.BACK, Layer.DOWN)
            for row in (1, 2)
            for col in (1, 2)
        ]

        # Count the fetches
        calls = []
        monkeypatch.setattr(centers, "fetch", lambda *args: calls.append(args[3]) or fetch(*args))

        # Assert
        with pytest.raises(ValueError, match=r"No route fills FRONT \(2, 1\) of the GREEN bar"):
            build_bar(cube, Color.GREEN, 2, ((Layer.FRONT,),), Layer.RIGHT, [], keep)
        assert calls == [CenterSearchResult(Layer.FRONT, 1, 2)]


class TestBuildCenter:
    def test_success(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that the whole center ends up on the target face, one bar and one insertion at a time.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(4, "z' Dw")

        # Build the center
        moves, result = build_center(cube, CENTERS_PLAN[0], [])

        # Assert
        assert moves == ["B2 Lw2 L2", "Rw2 R2", "Dw R2 Dw' R2", "Dw R2 Dw' R2"]
        assert _center_is(result, Layer.RIGHT, Color.YELLOW)

    def test_keeps_finished_centers(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that a center finished earlier is still intact once the next one is built.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube and build yellow on RIGHT
        cube = generate_cube(4, "z' Rw U2 Lw' F Dw")
        _, cube = build_center(cube, CENTERS_PLAN[0], [])
        keep = [Sticker(Layer.RIGHT, row, col, Color.YELLOW) for row in (1, 2) for col in (1, 2)]

        # Build white on LEFT
        _, result = build_center(cube, CENTERS_PLAN[1], keep)

        # Assert
        assert _center_is(result, Layer.LEFT, Color.WHITE)
        assert _center_is(result, Layer.RIGHT, Color.YELLOW)

    def test_odd_cube(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that on an odd cube the middle line is built first and then the bars, and that every
        fixed center is where it was once the center is built.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube: yellow is on RIGHT, then scattered
        cube = generate_cube(5, "z' Uw R Fw' D Bw2 L")

        # Build the center
        moves, result = build_center(cube, CENTERS_PLAN[0], [])
        line_moves, _ = build_middle_line(cube, Color.YELLOW, Layer.RIGHT, False, fixed_centers(cube))

        # Assert
        assert moves[: len(line_moves)] == line_moves
        assert _center_is(result, Layer.RIGHT, Color.YELLOW)
        assert fixed_centers(result) == fixed_centers(cube)


class TestBuildFirstFourCenters:
    def test_success(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that the returned algorithms, applied to the cube, build yellow, white, green and red on
        the faces the regrips leave them on, and that the cube itself is not turned.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate the cube
        cube = generate_cube(4, "Rw U2 Lw' F Dw")

        # Build the centers
        moves = build_first_four_centers(cube)
        result = trial(cube, " ".join(moves))

        # Assert
        assert moves[:4] == ["z'", "U Rw' R", "Dw R2 Dw' R2", "Lw L'"]
        assert all(_center_is(result, face, color) for color, face in FIRST_FOUR_FACES.items())
        assert cube.layers == generate_cube(4, "Rw U2 Lw' F Dw").layers

    # fmt: off
    @pytest.mark.parametrize("size", [4, 5, 6, 7, 8])
    # fmt: on
    def test_random_scrambles(self, generate_cube: Callable[[int, str], Cube], size: int) -> None:
        """
        Tests that the four centers are built from seeded random scrambles.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param size: The cube size
        :return: None
        """

        random.seed(size)

        for _ in range(5):
            # Scramble the cube
            scramble = str(Algorithm(Scrambler().generate_scramble(size)))
            cube = generate_cube(size, scramble)

            # Build the centers
            result = trial(cube, " ".join(build_first_four_centers(cube)))

            # Assert
            assert all(_center_is(result, face, color) for color, face in FIRST_FOUR_FACES.items()), scramble

    def test_lift_route_used(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that a DOWN piece is lifted rather than sliced out of the center being built, on the
        6x6 scramble whose red center needs it.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        random.seed(18)
        cube = generate_cube(6, str(Algorithm(Scrambler().generate_scramble(6))))

        # Assert
        assert any(move.startswith(f"{lift(6, 2, Direction.DOUBLE)} ") for move in build_first_four_centers(cube))
