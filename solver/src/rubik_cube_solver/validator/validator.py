# Python imports
from collections import Counter

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.enums.Color import Color


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
