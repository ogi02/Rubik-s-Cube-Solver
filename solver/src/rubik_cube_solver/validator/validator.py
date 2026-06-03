# Python imports
from collections import Counter

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.Layer import Layer

_VALID_CORNER_COLOR_SETS: frozenset[frozenset[Color]] = frozenset(
    {
        frozenset({Color.WHITE, Color.GREEN, Color.ORANGE}),
        frozenset({Color.WHITE, Color.GREEN, Color.RED}),
        frozenset({Color.WHITE, Color.BLUE, Color.ORANGE}),
        frozenset({Color.WHITE, Color.BLUE, Color.RED}),
        frozenset({Color.YELLOW, Color.GREEN, Color.ORANGE}),
        frozenset({Color.YELLOW, Color.GREEN, Color.RED}),
        frozenset({Color.YELLOW, Color.BLUE, Color.ORANGE}),
        frozenset({Color.YELLOW, Color.BLUE, Color.RED}),
    }
)

# Canonical CW sequence for each valid corner color set
_CORNER_CANONICAL_CW: dict[frozenset[Color], tuple[Color, Color, Color]] = {
    frozenset({Color.WHITE, Color.GREEN, Color.ORANGE}): (Color.WHITE, Color.GREEN, Color.ORANGE),
    frozenset({Color.WHITE, Color.GREEN, Color.RED}): (Color.WHITE, Color.RED, Color.GREEN),
    frozenset({Color.WHITE, Color.BLUE, Color.ORANGE}): (Color.WHITE, Color.ORANGE, Color.BLUE),
    frozenset({Color.WHITE, Color.BLUE, Color.RED}): (Color.WHITE, Color.BLUE, Color.RED),
    frozenset({Color.YELLOW, Color.GREEN, Color.ORANGE}): (Color.YELLOW, Color.ORANGE, Color.GREEN),
    frozenset({Color.YELLOW, Color.GREEN, Color.RED}): (Color.YELLOW, Color.GREEN, Color.RED),
    frozenset({Color.YELLOW, Color.BLUE, Color.ORANGE}): (Color.YELLOW, Color.BLUE, Color.ORANGE),
    frozenset({Color.YELLOW, Color.BLUE, Color.RED}): (Color.YELLOW, Color.RED, Color.BLUE),
}


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
    def _get_corners(cube: Cube) -> list[tuple[Color, Color, Color]]:
        """
        Returns a list of 8 corner tuples, one per corner, each containing the 3 sticker
        colors in the canonical clockwise face-sequence order.

        :param cube: The Cube instance
        :return: List of 8 corner color tuples
        """

        n = cube.size
        layers = cube.layers
        # Each entry: (face1_color, face2_color, face3_color) in CW order
        return [
            # UFL
            (layers[Layer.UP][n * (n - 1)], layers[Layer.FRONT][0], layers[Layer.LEFT][n - 1]),
            # UFR
            (layers[Layer.UP][n * n - 1], layers[Layer.RIGHT][0], layers[Layer.FRONT][n - 1]),
            # UBL
            (layers[Layer.UP][0], layers[Layer.LEFT][0], layers[Layer.BACK][n - 1]),
            # UBR
            (layers[Layer.UP][n - 1], layers[Layer.BACK][0], layers[Layer.RIGHT][n - 1]),
            # DFL
            (layers[Layer.DOWN][0], layers[Layer.LEFT][n * n - 1], layers[Layer.FRONT][n * (n - 1)]),
            # DFR
            (layers[Layer.DOWN][n - 1], layers[Layer.FRONT][n * n - 1], layers[Layer.RIGHT][n * (n - 1)]),
            # DBL
            (layers[Layer.DOWN][n * (n - 1)], layers[Layer.BACK][n * n - 1], layers[Layer.LEFT][n * (n - 1)]),
            # DBR
            (layers[Layer.DOWN][n * n - 1], layers[Layer.RIGHT][n * n - 1], layers[Layer.BACK][n * (n - 1)]),
        ]

    @staticmethod
    def _check_corner_validity(cube: Cube) -> None:
        """
        Validates that all 8 corner pieces are present exactly once with valid 3-color combinations.

        :param cube: The Cube instance to validate
        :return: None
        """

        corners = Validator._get_corners(cube)
        seen_color_sets: list[frozenset[Color]] = []

        for corner in corners:
            colors = frozenset(corner)
            if colors not in _VALID_CORNER_COLOR_SETS:
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

        corners = Validator._get_corners(cube)
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

        corners = Validator._get_corners(cube)

        for corner in corners:
            c0, c1, c2 = corner
            color_set = frozenset({c0, c1, c2})
            canonical = _CORNER_CANONICAL_CW[color_set]
            valid_rotations = {
                canonical,
                (canonical[1], canonical[2], canonical[0]),
                (canonical[2], canonical[0], canonical[1]),
            }
            if (c0, c1, c2) not in valid_rotations:
                raise ValueError(f"Invalid corner chirality for piece {color_set}.")
