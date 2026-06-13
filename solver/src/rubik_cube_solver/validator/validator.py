# Python imports
from collections import Counter

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.validator.validator_constants import (
    CENTER_COLORS_OPPOSITES,
    CENTER_LAYER_OPPOSITES,
    CORNER_CANONICAL_CW,
    EDGE_CANONICAL_ORIENTATION,
    VALID_CORNER_COLOR_SETS,
    VALID_EDGE_COLOR_SETS,
)
from rubik_cube_solver.validator.validator_utils import get_centers, get_corners, get_edges, get_wing_edges


class Validator:
    """
    Validator class that validates the state of a Rubik's Cube.
    """

    def validate(self, cube: Cube) -> None:
        """
        Validates the state of a Rubik's Cube.
        Raises ValueError if the cube state is invalid.

        :param cube: The Cube instance to validate
        :return: None
        """

        self._check_size(cube)
        self._check_color_count(cube)
        self._check_corner_validity(cube)
        self._check_corner_orientation(cube)
        self._check_corner_chirality(cube)

        if cube.size % 2 == 1:
            self._check_center_uniqueness(cube)
            self._check_center_opposites(cube)
            self._check_edge_validity(cube)
            self._check_edge_flip_parity(cube)
            self._check_permutation_parity(cube)

        if cube.size >= 4:
            self._check_center_count_big(cube)
            self._check_wing_edge_validity(cube)

    @staticmethod
    def _check_size(cube: Cube) -> None:
        """
        Validates that the cube size is at least 2.

        :param cube: The Cube instance to validate
        :return: None
        """

        if cube.size < 2:
            raise ValueError("Cube size must be at least 2.")

    @staticmethod
    def _check_color_count(cube: Cube) -> None:
        """
        Validates that each of the 6 colors appears exactly N^2 times
        across all stickers.

        :param cube: The Cube instance to validate
        :return: None
        """

        expected_count = cube.size * cube.size
        all_stickers = [sticker for face in cube.layers.values() for sticker in face]
        color_counts = Counter(all_stickers)

        for color in Color:
            actual_count = color_counts.get(color, 0)
            if actual_count != expected_count:
                raise ValueError(
                    f"Invalid color count for {color.name}: expected {expected_count}, got {actual_count}."
                )

    @staticmethod
    def _check_corner_validity(cube: Cube) -> None:
        """
        Validates that all 8 corner pieces are present exactly once with valid 3-color combinations.

        :param cube: The Cube instance to validate
        :return: None
        """

        corners = get_corners(cube)
        seen_color_sets: list[frozenset[Color]] = []

        for corner in corners:
            colors = frozenset(corner)
            if colors not in VALID_CORNER_COLOR_SETS:
                raise ValueError(f"Invalid corner piece: {colors}.")
            if colors in seen_color_sets:
                raise ValueError(f"Duplicate corner piece: {colors}.")
            seen_color_sets.append(colors)

    @staticmethod
    def _check_corner_orientation(cube: Cube) -> None:
        """
        Validates that the sum of all 8 corner orientations is divisible by 3.

        :param cube: The Cube instance to validate
        :return: None
        """

        corners = get_corners(cube)
        ud_colors = {Color.WHITE, Color.YELLOW}
        total = 0

        for corner in corners:
            c0, c1, c2 = corner
            if c0 in ud_colors:
                total += 0
            elif c1 in ud_colors:
                total += 1
            elif c2 in ud_colors:
                total += 2
            else:
                raise ValueError(f"Corner has no UP/DOWN color: {corner}.")

        if total % 3 != 0:
            raise ValueError(
                f"Invalid corner orientation parity: sum of orientations is {total}, expected a multiple of 3."
            )

    @staticmethod
    def _check_corner_chirality(cube: Cube) -> None:
        """
        Validates that each corner's stickers appear in the correct clockwise cyclic order.

        :param cube: The Cube instance to validate
        :return: None
        """

        corners = get_corners(cube)

        for corner in corners:
            c0, c1, c2 = corner
            color_set = frozenset({c0, c1, c2})
            canonical = CORNER_CANONICAL_CW[color_set]
            valid_rotations = {
                canonical,
                (canonical[1], canonical[2], canonical[0]),
                (canonical[2], canonical[0], canonical[1]),
            }
            if (c0, c1, c2) not in valid_rotations:
                raise ValueError(f"Invalid corner chirality for piece {color_set}.")

    @staticmethod
    def _check_center_uniqueness(cube: Cube) -> None:
        """
        Validates that all 6 center stickers of an odd sized cube are distinct colors.

        :param cube: The Cube instance to validate
        :return: None
        """

        seen_colors: list[Color] = []
        for face in Layer:
            center_color = cube.layers[face][cube.size // 2]
            if center_color in seen_colors:
                raise ValueError(f"Duplicate center piece: {center_color}.")
            seen_colors.append(center_color)

    @staticmethod
    def _check_center_opposites(cube: Cube) -> None:
        """
        Validates that all 6 center stickers of an odd sized cube have correct opposite colors.

        :param cube: The Cube instance to validate
        :return: None
        """

        for face in Layer:
            center_color = cube.layers[face][cube.size // 2]
            opposite_color = cube.layers[CENTER_LAYER_OPPOSITES[face]][cube.size // 2]
            if CENTER_COLORS_OPPOSITES[center_color] != opposite_color:
                raise ValueError(f"Invalid opposite color of {center_color}: {opposite_color}.")

    @staticmethod
    def _check_center_count_big(cube: Cube) -> None:
        """
        Validates that each center piece type appears exactly 4 times for big cubes (N >= 4).

        :param cube: The Cube instance to validate
        :return: None
        """

        centers = get_centers(cube)
        counter: Counter = Counter()

        for center in centers:
            counter[center] += 1

        for piece, count in counter.items():
            color, row, col = piece
            if count != 4:
                raise ValueError(
                    f"Invalid center piece count for {color} at row {row}, col {col}: expected 4, got {count}."
                )

    @staticmethod
    def _check_edge_validity(cube: Cube) -> None:
        """
        Validates that all 12 edge pieces are present exactly once with valid 2-color combinations.

        :param cube: The Cube instance to validate
        :return: None
        """

        edges = get_edges(cube)
        seen_color_sets: list[frozenset[Color]] = []

        for edge in edges:
            colors = frozenset(edge)
            if colors not in VALID_EDGE_COLOR_SETS:
                raise ValueError(f"Invalid edge piece: {colors}.")
            if colors in seen_color_sets:
                raise ValueError(f"Duplicate edge piece: {colors}.")
            seen_color_sets.append(colors)

    @staticmethod
    def _check_wing_edge_validity(cube: Cube) -> None:
        """
        Validates that all directed wing edge pieces are present exactly once for big cubes (N >= 4).

        :param cube: The Cube instance to validate
        :return: None
        """

        wing_edges = get_wing_edges(cube)
        seen_wing_edges: list[tuple[int, Color, Color]] = []

        for wing_edge in wing_edges:
            _, primary_color, secondary_color = wing_edge
            wing_edge_colors = frozenset({primary_color, secondary_color})
            if wing_edge_colors not in VALID_EDGE_COLOR_SETS:
                raise ValueError(f"Invalid wing edge piece: {wing_edge_colors}.")
            if wing_edge in seen_wing_edges:
                raise ValueError(f"Duplicate wing edge piece: {wing_edge}.")
            seen_wing_edges.append(wing_edge)

    @staticmethod
    def _check_edge_flip_parity(cube: Cube) -> None:
        """
        Validates that the sum of all 12 edge orientations is divisible by 2.

        :param cube: The Cube instance to validate
        :return: None
        """

        edges = get_edges(cube)
        total = 0

        for c1, c2 in edges:
            primary_color = EDGE_CANONICAL_ORIENTATION[frozenset({c1, c2})]
            if c1 == primary_color:
                total += 0
            else:
                total += 1

        if total % 2 != 0:
            raise ValueError(f"Invalid edge flip parity: sum of orientations is {total}, expected a multiple of 2.")

    @staticmethod
    def _check_permutation_parity(cube: Cube) -> None:
        """
        Validates that corner and edge permutations share the same parity (both even or both odd).

        :param cube: The Cube instance to validate
        :return: None
        """

        canonical_corners: list[frozenset[Color]] = [
            frozenset({Color.WHITE, Color.GREEN, Color.ORANGE}),  # UFL
            frozenset({Color.WHITE, Color.GREEN, Color.RED}),  # UFR
            frozenset({Color.WHITE, Color.ORANGE, Color.BLUE}),  # UBL
            frozenset({Color.WHITE, Color.BLUE, Color.RED}),  # UBR
            frozenset({Color.YELLOW, Color.ORANGE, Color.GREEN}),  # DFL
            frozenset({Color.YELLOW, Color.GREEN, Color.RED}),  # DFR
            frozenset({Color.YELLOW, Color.BLUE, Color.ORANGE}),  # DBL
            frozenset({Color.YELLOW, Color.BLUE, Color.RED}),  # DBR
        ]

        canonical_edges: list[frozenset[Color]] = [
            frozenset({Color.WHITE, Color.GREEN}),  # UF
            frozenset({Color.WHITE, Color.BLUE}),  # UB
            frozenset({Color.WHITE, Color.ORANGE}),  # UL
            frozenset({Color.WHITE, Color.RED}),  # UR
            frozenset({Color.YELLOW, Color.GREEN}),  # DF
            frozenset({Color.YELLOW, Color.BLUE}),  # DB
            frozenset({Color.YELLOW, Color.ORANGE}),  # DL
            frozenset({Color.YELLOW, Color.RED}),  # DR
            frozenset({Color.GREEN, Color.ORANGE}),  # FL
            frozenset({Color.GREEN, Color.RED}),  # FR
            frozenset({Color.BLUE, Color.ORANGE}),  # BL
            frozenset({Color.BLUE, Color.RED}),  # BR
        ]

        corners = get_corners(cube)
        corner_perm = [canonical_corners.index(frozenset(corner)) for corner in corners]

        edges = get_edges(cube)
        edge_perm = [canonical_edges.index(frozenset(edge)) for edge in edges]

        def count_inversions(perm: list[int]) -> int:
            inversions = 0
            for i in range(len(perm)):
                for j in range(i + 1, len(perm)):
                    if perm[i] > perm[j]:
                        inversions += 1
            return inversions

        corner_parity = count_inversions(corner_perm) % 2
        edge_parity = count_inversions(edge_perm) % 2

        if corner_parity != edge_parity:
            raise ValueError("Invalid permutation parity: corner and edge permutations have different parities.")
