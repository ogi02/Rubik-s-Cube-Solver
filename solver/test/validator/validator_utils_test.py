# Python imports
import pytest

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.cube_rotation.rotator import Rotator
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.validator.validator import Validator
from rubik_cube_solver.validator.validator_constants import (
    CORNER_SLOT_LAYERS,
    EDGE_SLOT_LAYERS,
    VALID_CORNER_COLOR_SETS,
    VALID_EDGE_COLOR_SETS,
)
from rubik_cube_solver.validator.validator_utils import (
    face_center_color,
    get_canonical_pieces,
    get_centers,
    get_corners,
    get_edges,
    get_index_formulas,
    get_wing_edges,
    wing_edge_indices,
)

# Canonical corner slot values for a solved Cube(3) in slot order UFL, UFR, UBL, UBR, DFL, DFR, DBL, DBR
SOLVED_CANONICAL_CORNERS: list[frozenset[Color]] = [
    frozenset({Color.WHITE, Color.GREEN, Color.ORANGE}),
    frozenset({Color.WHITE, Color.GREEN, Color.RED}),
    frozenset({Color.WHITE, Color.ORANGE, Color.BLUE}),
    frozenset({Color.WHITE, Color.BLUE, Color.RED}),
    frozenset({Color.YELLOW, Color.ORANGE, Color.GREEN}),
    frozenset({Color.YELLOW, Color.GREEN, Color.RED}),
    frozenset({Color.YELLOW, Color.BLUE, Color.ORANGE}),
    frozenset({Color.YELLOW, Color.BLUE, Color.RED}),
]

# Canonical edge slot values for a solved Cube(3) in slot order UF, UB, UL, UR, DF, DB, DL, DR, FL, FR, BL, BR
SOLVED_CANONICAL_EDGES: list[frozenset[Color]] = [
    frozenset({Color.WHITE, Color.GREEN}),
    frozenset({Color.WHITE, Color.BLUE}),
    frozenset({Color.WHITE, Color.ORANGE}),
    frozenset({Color.WHITE, Color.RED}),
    frozenset({Color.YELLOW, Color.GREEN}),
    frozenset({Color.YELLOW, Color.BLUE}),
    frozenset({Color.YELLOW, Color.ORANGE}),
    frozenset({Color.YELLOW, Color.RED}),
    frozenset({Color.GREEN, Color.ORANGE}),
    frozenset({Color.GREEN, Color.RED}),
    frozenset({Color.BLUE, Color.ORANGE}),
    frozenset({Color.BLUE, Color.RED}),
]

# Canonical corner slot values for a Cube(3) reoriented by "x", same slot order as above
ROTATED_X_CANONICAL_CORNERS: list[frozenset[Color]] = [
    frozenset({Color.YELLOW, Color.GREEN, Color.ORANGE}),
    frozenset({Color.YELLOW, Color.GREEN, Color.RED}),
    frozenset({Color.WHITE, Color.GREEN, Color.ORANGE}),
    frozenset({Color.WHITE, Color.GREEN, Color.RED}),
    frozenset({Color.YELLOW, Color.BLUE, Color.ORANGE}),
    frozenset({Color.YELLOW, Color.BLUE, Color.RED}),
    frozenset({Color.WHITE, Color.BLUE, Color.ORANGE}),
    frozenset({Color.WHITE, Color.BLUE, Color.RED}),
]

# Canonical edge slot values for a Cube(3) reoriented by "x", same slot order as above
ROTATED_X_CANONICAL_EDGES: list[frozenset[Color]] = [
    frozenset({Color.YELLOW, Color.GREEN}),
    frozenset({Color.WHITE, Color.GREEN}),
    frozenset({Color.GREEN, Color.ORANGE}),
    frozenset({Color.GREEN, Color.RED}),
    frozenset({Color.YELLOW, Color.BLUE}),
    frozenset({Color.WHITE, Color.BLUE}),
    frozenset({Color.BLUE, Color.ORANGE}),
    frozenset({Color.BLUE, Color.RED}),
    frozenset({Color.YELLOW, Color.ORANGE}),
    frozenset({Color.YELLOW, Color.RED}),
    frozenset({Color.WHITE, Color.ORANGE}),
    frozenset({Color.WHITE, Color.RED}),
]


class TestFaceCenterColor:
    # fmt: off
    @pytest.mark.parametrize(
        "layer, expected_color", [
            (Layer.UP,    Color.WHITE),
            (Layer.DOWN,  Color.YELLOW),
            (Layer.LEFT,  Color.ORANGE),
            (Layer.RIGHT, Color.RED),
            (Layer.FRONT, Color.GREEN),
            (Layer.BACK,  Color.BLUE),
        ]
    )
    # fmt: on
    def test_success(self, layer: Layer, expected_color: Color) -> None:
        """
        Test that face_center_color returns each face's center sticker color on a solved cube.

        :param layer: The face to read the center sticker of
        :param expected_color: The expected center sticker color
        :return: None
        """

        cube = Cube(3)
        assert face_center_color(cube, layer) == expected_color

    # fmt: off
    @pytest.mark.parametrize(
        "layer, expected_color", [
            (Layer.UP,    Color.GREEN),
            (Layer.DOWN,  Color.BLUE),
            (Layer.FRONT, Color.YELLOW),
            (Layer.BACK,  Color.WHITE),
            (Layer.LEFT,  Color.ORANGE),
            (Layer.RIGHT, Color.RED),
        ]
    )
    # fmt: on
    def test_success_after_rotation(self, layer: Layer, expected_color: Color) -> None:
        """
        Test that face_center_color returns the rotated center sticker color after a whole-cube rotation.

        :param layer: The face to read the center sticker of
        :param expected_color: The expected center sticker color after the cube is rotated with "x"
        :return: None
        """

        cube = Cube(3)
        Rotator(cube).apply(Algorithm.from_str("x"))
        assert face_center_color(cube, layer) == expected_color


class TestGetCanonicalPieces:
    def test_success_solved_corners(self) -> None:
        """
        Test that get_canonical_pieces reproduces the old hardcoded corner reference table for a solved cube.

        :return: None
        """

        cube = Cube(3)
        assert get_canonical_pieces(cube, CORNER_SLOT_LAYERS) == SOLVED_CANONICAL_CORNERS

    def test_success_solved_edges(self) -> None:
        """
        Test that get_canonical_pieces reproduces the old hardcoded edge reference table for a solved cube.

        :return: None
        """

        cube = Cube(3)
        assert get_canonical_pieces(cube, EDGE_SLOT_LAYERS) == SOLVED_CANONICAL_EDGES

    def test_success_rotated_corners(self) -> None:
        """
        Test that get_canonical_pieces returns the correspondingly rotated corner sets after an "x" rotation.

        :return: None
        """

        cube = Cube(3)
        Rotator(cube).apply(Algorithm.from_str("x"))
        assert get_canonical_pieces(cube, CORNER_SLOT_LAYERS) == ROTATED_X_CANONICAL_CORNERS

    def test_success_rotated_edges(self) -> None:
        """
        Test that get_canonical_pieces returns the correspondingly rotated edge sets after an "x" rotation.

        :return: None
        """

        cube = Cube(3)
        Rotator(cube).apply(Algorithm.from_str("x"))
        assert get_canonical_pieces(cube, EDGE_SLOT_LAYERS) == ROTATED_X_CANONICAL_EDGES


class TestGetCorners:
    def test_success(self, validator: Validator) -> None:
        """
        Test that get_corners returns the expected corners.

        :param validator: Fixture of a Validator instance
        :return: None
        """

        cube = Cube(3)
        corners = get_corners(cube)
        expected_corners = VALID_CORNER_COLOR_SETS

        assert len(corners) == len(expected_corners)
        for corner in corners:
            assert isinstance(corner, tuple)
            assert frozenset(corner) in expected_corners


class TestGetIndexFormulas:
    # fmt: off
    @pytest.mark.parametrize(
        "cube_size, row, col, expected_center_piece_indices",
        [
            # 4x4
            (4, 1, 1, [5,  6,  9, 10]),
            (4, 1, 2, [5,  6,  9, 10]),
            (4, 2, 1, [5,  6,  9, 10]),
            (4, 2, 2, [5,  6,  9, 10]),
            # 5x5
            (5, 1, 1, [6,  8, 16, 18]),
            (5, 1, 2, [7,  11, 13, 17]),
            (5, 1, 3, [6,  8, 16, 18]),
            (5, 2, 1, [7,  11, 13, 17]),
            (5, 2, 2, [12, 12, 12, 12]),
            (5, 2, 3, [7,  11, 13, 17]),
            (5, 3, 1, [6,   8, 16, 18]),
            (5, 3, 2, [7,  11, 13, 17]),
            (5, 3, 3, [6,   8, 16, 18]),
            # 6x6
            (6, 1, 1, [7,  10, 25, 28]),
            (6, 1, 2, [8,  16, 19, 27]),
            (6, 1, 3, [9,  13, 22, 26]),
            (6, 1, 4, [7,  10, 25, 28]),
            (6, 2, 1, [9,  13, 22, 26]),
            (6, 2, 2, [14, 15, 20, 21]),
            (6, 2, 3, [14, 15, 20, 21]),
            (6, 2, 4, [8,  16, 19, 27]),
            (6, 3, 1, [8,  16, 19, 27]),
            (6, 3, 2, [14, 15, 20, 21]),
            (6, 3, 3, [14, 15, 20, 21]),
            (6, 3, 4, [9,  13, 22, 26]),
            (6, 4, 1, [7,  10, 25, 28]),
            (6, 4, 2, [9,  13, 22, 26]),
            (6, 4, 3, [8,  16, 19, 27]),
            (6, 4, 4, [7,  10, 25, 28]),
            # 7x7
            (7, 1, 1, [8,  12, 36, 40]),
            (7, 1, 2, [9,  19, 29, 39]),
            (7, 1, 3, [10, 22, 26, 38]),
            (7, 1, 4, [11, 15, 33, 37]),
            (7, 1, 5, [8,  12, 36, 40]),
            (7, 2, 1, [11, 15, 33, 37]),
            (7, 2, 2, [16, 18, 30, 32]),
            (7, 2, 3, [17, 23, 25, 31]),
            (7, 2, 4, [16, 18, 30, 32]),
            (7, 2, 5, [9,  19, 29, 39]),
            (7, 3, 1, [10, 22, 26, 38]),
            (7, 3, 2, [17, 23, 25, 31]),
            (7, 3, 3, [24, 24, 24, 24]),
            (7, 3, 4, [17, 23, 25, 31]),
            (7, 3, 5, [10, 22, 26, 38]),
            (7, 4, 1, [9,  19, 29, 39]),
            (7, 4, 2, [16, 18, 30, 32]),
            (7, 4, 3, [17, 23, 25, 31]),
            (7, 4, 4, [16, 18, 30, 32]),
            (7, 4, 5, [11, 15, 33, 37]),
            (7, 5, 1, [8,  12, 36, 40]),
            (7, 5, 2, [11, 15, 33, 37]),
            (7, 5, 3, [10, 22, 26, 38]),
            (7, 5, 4, [9,  19, 29, 39]),
            (7, 5, 5, [8,  12, 36, 40]),
        ]
    )
    # fmt: on
    def test_success(
        self, validator: Validator, cube_size: int, row: int, col: int, expected_center_piece_indices: list[int]
    ) -> None:
        """
        Test that _get_index_formulas returns the expected indices for the centers based on the provided row and column.

        :param validator: Fixture of a Validator instance
        :param cube_size: The size of the cube to validate
        :param row: The row to validate against
        :param col: The column to validate against
        :param expected_center_piece_indices: The expected center pieces
        """

        actual_center_piece_indices = get_index_formulas(cube_size, row, col)
        assert sorted(actual_center_piece_indices) == sorted(expected_center_piece_indices)


class TestGetCenters:
    @pytest.mark.parametrize("cube_size", [4, 5, 6, 7])
    def test_success(self, validator: Validator, cube_size: int, generate_expected_centers) -> None:
        """
        Test that get_centers returns the expected centers for a solved big cube.

        :param validator: Fixture of a Validator instance
        :param cube_size: The size of the cube to validate
        :param generate_expected_centers: Fixture to generate the expected centers
        """

        cube = Cube(cube_size)
        centers = get_centers(cube)

        assert centers == generate_expected_centers(cube_size)


class TestGetEdges:
    @pytest.mark.parametrize("cube_size", [3, 5, 7])
    def test_success(self, validator: Validator, cube_size: int) -> None:
        """
        Test that get_edges returns 12 edge tuples with correct sticker colors for a solved odd sized cube.

        :param validator: Fixture of a Validator instance
        :param cube_size: The size of the cube to validate
        :return: None
        """

        cube = Cube(cube_size)
        edges = get_edges(cube)
        expected_edges = VALID_EDGE_COLOR_SETS

        assert len(edges) == len(expected_edges)
        for edge in edges:
            assert isinstance(edge, tuple)
            assert frozenset(edge) in expected_edges


class TestWingEdgeIndices:
    # fmt: off
    @pytest.mark.parametrize(
        "primary_layer, secondary_layer, cube_size, wing_index, expected_primary_index, expected_secondary_index",
        [
            # 4x4
            (Layer.UP,    Layer.LEFT,  4, 1,  4,  1),
            (Layer.UP,    Layer.RIGHT, 4, 1, 11,  1),
            (Layer.UP,    Layer.FRONT, 4, 1, 13,  1),
            (Layer.UP,    Layer.BACK,  4, 1,  2,  1),
            (Layer.DOWN,  Layer.LEFT,  4, 1,  4, 14),
            (Layer.DOWN,  Layer.RIGHT, 4, 1, 11, 14),
            (Layer.DOWN,  Layer.FRONT, 4, 1,  2, 14),
            (Layer.DOWN,  Layer.BACK,  4, 1, 13, 14),
            (Layer.LEFT,  Layer.UP,    4, 1,  2,  8),
            (Layer.LEFT,  Layer.DOWN,  4, 1, 13,  8),
            (Layer.LEFT,  Layer.FRONT, 4, 1, 11,  8),
            (Layer.LEFT,  Layer.BACK,  4, 1,  4,  7),
            (Layer.RIGHT, Layer.UP,    4, 1,  2,  7),
            (Layer.RIGHT, Layer.DOWN,  4, 1, 13,  7),
            (Layer.RIGHT, Layer.FRONT, 4, 1,  4,  7),
            (Layer.RIGHT, Layer.BACK,  4, 1, 11,  8),
            (Layer.FRONT, Layer.UP,    4, 1,  2, 14),
            (Layer.FRONT, Layer.DOWN,  4, 1, 13,  1),
            (Layer.FRONT, Layer.LEFT,  4, 1,  4,  7),
            (Layer.FRONT, Layer.RIGHT, 4, 1, 11,  8),
            (Layer.BACK,  Layer.UP,    4, 1,  2,  1),
            (Layer.BACK,  Layer.DOWN,  4, 1, 13, 14),
            (Layer.BACK,  Layer.LEFT,  4, 1, 11,  8),
            (Layer.BACK,  Layer.RIGHT, 4, 1,  4,  7),
            # 5x5
            (Layer.UP,    Layer.LEFT,  5, 1,  5,  1),
            (Layer.UP,    Layer.RIGHT, 5, 1, 19,  1),
            (Layer.UP,    Layer.FRONT, 5, 1, 21,  1),
            (Layer.UP,    Layer.BACK,  5, 1,  3,  1),
            (Layer.DOWN,  Layer.LEFT,  5, 1,  5, 23),
            (Layer.DOWN,  Layer.RIGHT, 5, 1, 19, 23),
            (Layer.DOWN,  Layer.FRONT, 5, 1,  3, 23),
            (Layer.DOWN,  Layer.BACK,  5, 1, 21, 23),
            (Layer.LEFT,  Layer.UP,    5, 1,  3, 15),
            (Layer.LEFT,  Layer.DOWN,  5, 1, 21, 15),
            (Layer.LEFT,  Layer.FRONT, 5, 1, 19, 15),
            (Layer.LEFT,  Layer.BACK,  5, 1,  5,  9),
            (Layer.RIGHT, Layer.UP,    5, 1,  3,  9),
            (Layer.RIGHT, Layer.DOWN,  5, 1, 21,  9),
            (Layer.RIGHT, Layer.FRONT, 5, 1,  5,  9),
            (Layer.RIGHT, Layer.BACK,  5, 1, 19, 15),
            (Layer.FRONT, Layer.UP,    5, 1,  3, 23),
            (Layer.FRONT, Layer.DOWN,  5, 1, 21,  1),
            (Layer.FRONT, Layer.LEFT,  5, 1,  5,  9),
            (Layer.FRONT, Layer.RIGHT, 5, 1, 19, 15),
            (Layer.BACK,  Layer.UP,    5, 1,  3,  1),
            (Layer.BACK,  Layer.DOWN,  5, 1, 21, 23),
            (Layer.BACK,  Layer.LEFT,  5, 1, 19, 15),
            (Layer.BACK,  Layer.RIGHT, 5, 1,  5,  9),
            # 6x6
            (Layer.UP,    Layer.LEFT,  6, 1,  6,  1),
            (Layer.UP,    Layer.RIGHT, 6, 1, 29,  1),
            (Layer.UP,    Layer.FRONT, 6, 1, 31,  1),
            (Layer.UP,    Layer.BACK,  6, 1,  4,  1),
            (Layer.DOWN,  Layer.LEFT,  6, 1,  6, 34),
            (Layer.DOWN,  Layer.RIGHT, 6, 1, 29, 34),
            (Layer.DOWN,  Layer.FRONT, 6, 1,  4, 34),
            (Layer.DOWN,  Layer.BACK,  6, 1, 31, 34),
            (Layer.LEFT,  Layer.UP,    6, 1,  4, 24),
            (Layer.LEFT,  Layer.DOWN,  6, 1, 31, 24),
            (Layer.LEFT,  Layer.FRONT, 6, 1, 29, 24),
            (Layer.LEFT,  Layer.BACK,  6, 1,  6, 11),
            (Layer.RIGHT, Layer.UP,    6, 1,  4, 11),
            (Layer.RIGHT, Layer.DOWN,  6, 1, 31, 11),
            (Layer.RIGHT, Layer.FRONT, 6, 1,  6, 11),
            (Layer.RIGHT, Layer.BACK,  6, 1, 29, 24),
            (Layer.FRONT, Layer.UP,    6, 1,  4, 34),
            (Layer.FRONT, Layer.DOWN,  6, 1, 31,  1),
            (Layer.FRONT, Layer.LEFT,  6, 1,  6, 11),
            (Layer.FRONT, Layer.RIGHT, 6, 1, 29, 24),
            (Layer.BACK,  Layer.UP,    6, 1,  4,  1),
            (Layer.BACK,  Layer.DOWN,  6, 1, 31, 34),
            (Layer.BACK,  Layer.LEFT,  6, 1, 29, 24),
            (Layer.BACK,  Layer.RIGHT, 6, 1,  6, 11),
            (Layer.UP,    Layer.LEFT,  6, 2, 12,  2),
            (Layer.UP,    Layer.RIGHT, 6, 2, 23,  2),
            (Layer.UP,    Layer.FRONT, 6, 2, 32,  2),
            (Layer.UP,    Layer.BACK,  6, 2,  3,  2),
            (Layer.DOWN,  Layer.LEFT,  6, 2, 12, 33),
            (Layer.DOWN,  Layer.RIGHT, 6, 2, 23, 33),
            (Layer.DOWN,  Layer.FRONT, 6, 2,  3, 33),
            (Layer.DOWN,  Layer.BACK,  6, 2, 32, 33),
            (Layer.LEFT,  Layer.UP,    6, 2,  3, 18),
            (Layer.LEFT,  Layer.DOWN,  6, 2, 32, 18),
            (Layer.LEFT,  Layer.FRONT, 6, 2, 23, 18),
            (Layer.LEFT,  Layer.BACK,  6, 2, 12, 17),
            (Layer.RIGHT, Layer.UP,    6, 2,  3, 17),
            (Layer.RIGHT, Layer.DOWN,  6, 2, 32, 17),
            (Layer.RIGHT, Layer.FRONT, 6, 2, 12, 17),
            (Layer.RIGHT, Layer.BACK,  6, 2, 23, 18),
            (Layer.FRONT, Layer.UP,    6, 2,  3, 33),
            (Layer.FRONT, Layer.DOWN,  6, 2, 32,  2),
            (Layer.FRONT, Layer.LEFT,  6, 2, 12, 17),
            (Layer.FRONT, Layer.RIGHT, 6, 2, 23, 18),
            (Layer.BACK,  Layer.UP,    6, 2,  3,  2),
            (Layer.BACK,  Layer.DOWN,  6, 2, 32, 33),
            (Layer.BACK,  Layer.LEFT,  6, 2, 23, 18),
            (Layer.BACK,  Layer.RIGHT, 6, 2, 12, 17),
            # 7x7
            (Layer.UP,    Layer.LEFT,  7, 1,  7,  1),
            (Layer.UP,    Layer.RIGHT, 7, 1, 41,  1),
            (Layer.UP,    Layer.FRONT, 7, 1, 43,  1),
            (Layer.UP,    Layer.BACK,  7, 1,  5,  1),
            (Layer.DOWN,  Layer.LEFT,  7, 1,  7, 47),
            (Layer.DOWN,  Layer.RIGHT, 7, 1, 41, 47),
            (Layer.DOWN,  Layer.FRONT, 7, 1,  5, 47),
            (Layer.DOWN,  Layer.BACK,  7, 1, 43, 47),
            (Layer.LEFT,  Layer.UP,    7, 1,  5, 35),
            (Layer.LEFT,  Layer.DOWN,  7, 1, 43, 35),
            (Layer.LEFT,  Layer.FRONT, 7, 1, 41, 35),
            (Layer.LEFT,  Layer.BACK,  7, 1,  7, 13),
            (Layer.RIGHT, Layer.UP,    7, 1,  5, 13),
            (Layer.RIGHT, Layer.DOWN,  7, 1, 43, 13),
            (Layer.RIGHT, Layer.FRONT, 7, 1,  7, 13),
            (Layer.RIGHT, Layer.BACK,  7, 1, 41, 35),
            (Layer.FRONT, Layer.UP,    7, 1,  5, 47),
            (Layer.FRONT, Layer.DOWN,  7, 1, 43,  1),
            (Layer.FRONT, Layer.LEFT,  7, 1,  7, 13),
            (Layer.FRONT, Layer.RIGHT, 7, 1, 41, 35),
            (Layer.BACK,  Layer.UP,    7, 1,  5,  1),
            (Layer.BACK,  Layer.DOWN,  7, 1, 43, 47),
            (Layer.BACK,  Layer.LEFT,  7, 1, 41, 35),
            (Layer.BACK,  Layer.RIGHT, 7, 1,  7, 13),
            (Layer.UP,    Layer.LEFT,  7, 2, 14,  2),
            (Layer.UP,    Layer.RIGHT, 7, 2, 34,  2),
            (Layer.UP,    Layer.FRONT, 7, 2, 44,  2),
            (Layer.UP,    Layer.BACK,  7, 2,  4,  2),
            (Layer.DOWN,  Layer.LEFT,  7, 2, 14, 46),
            (Layer.DOWN,  Layer.RIGHT, 7, 2, 34, 46),
            (Layer.DOWN,  Layer.FRONT, 7, 2,  4, 46),
            (Layer.DOWN,  Layer.BACK,  7, 2, 44, 46),
            (Layer.LEFT,  Layer.UP,    7, 2,  4, 28),
            (Layer.LEFT,  Layer.DOWN,  7, 2, 44, 28),
            (Layer.LEFT,  Layer.FRONT, 7, 2, 34, 28),
            (Layer.LEFT,  Layer.BACK,  7, 2, 14, 20),
            (Layer.RIGHT, Layer.UP,    7, 2,  4, 20),
            (Layer.RIGHT, Layer.DOWN,  7, 2, 44, 20),
            (Layer.RIGHT, Layer.FRONT, 7, 2, 14, 20),
            (Layer.RIGHT, Layer.BACK,  7, 2, 34, 28),
            (Layer.FRONT, Layer.UP,    7, 2,  4, 46),
            (Layer.FRONT, Layer.DOWN,  7, 2, 44,  2),
            (Layer.FRONT, Layer.LEFT,  7, 2, 14, 20),
            (Layer.FRONT, Layer.RIGHT, 7, 2, 34, 28),
            (Layer.BACK,  Layer.UP,    7, 2,  4,  2),
            (Layer.BACK,  Layer.DOWN,  7, 2, 44, 46),
            (Layer.BACK,  Layer.LEFT,  7, 2, 34, 28),
            (Layer.BACK,  Layer.RIGHT, 7, 2, 14, 20),
        ]
    )
    # fmt: on
    def test_success(
        self,
        primary_layer: Layer,
        secondary_layer: Layer,
        cube_size: int,
        wing_index: int,
        expected_primary_index: int,
        expected_secondary_index: int,
    ) -> None:
        """
        Test that wing_edge_indices returns the expected indices based on the primary layer and secondary layer.

        :param primary_layer: The primary layer
        :param secondary_layer: The secondary layer
        :param cube_size: The size of the cube to validate
        :param wing_index: The wing index to use
        :param expected_primary_index: The expected primary index
        :param expected_secondary_index: The expected secondary index
        """

        actual = wing_edge_indices(primary_layer, secondary_layer, cube_size, wing_index)
        assert actual == (expected_primary_index, expected_secondary_index)


class TestGetWingEdges:
    @pytest.mark.parametrize("cube_size", [4, 5, 6, 7])
    def test_success(self, validator: Validator, cube_size: int, generate_expected_wing_edges) -> None:
        """
        Test that get_wing_edges returns the expected set of wing edges based on the cube size.

        :param validator: Fixture of a Validator instance
        :param cube_size: The size of the cube to validate
        :param generate_expected_wing_edges: Fixture to generate expected wing edges
        :return: None
        """

        cube = Cube(cube_size)
        wing_edges = get_wing_edges(cube)

        assert wing_edges == generate_expected_wing_edges(cube_size)
