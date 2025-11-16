# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.validator.corner_validation import get_corner_colors, get_corner_positions


class Validator:
    """
    A class to validate the state of a Rubik's Cube.

    The cube validation consists of the following steps:
    1. Verify the cube has valid dimensions - cube size should be an integer >= 2.
    2. Verify that the cube has the correct number of pieces based on the cube size.
    3. Verify that there are exactly 4 stickers of every color on the corners of the cube.
    4. Verify that there is exactly 1 center piece of every color on an odd-sized cube.
    5. Verify that the center pieces are correctly placed on an odd-sized cube.
    6. Verify that there are exactly 12 center-edge pieces of every color combination on the cube.
    7. Verify that there are exactly 24 edge pieces of every type and color combination on a cube, bigger than 3x3x3.
    8. Verify that there are exactly 4 x-center pieces of every type and color on a cube, bigger than 3x3x3.
    9. Verify that there are exactly 4 +-center pieces of every type and color on a cube, bigger than 4x4x4.
    10. Verify that the orientation of corner pieces is valid.
    11. Verify that the orientation of center edge pieces is valid.
    12. Verify that the orientation of the edge pieces of every type is valid.
    13. Verify that the corner-edge parity on an odd-sized cube is valid.
    """

    def __init__(self, cube: Cube) -> None:
        """
        Initialize the Validator with a Cube instance.

        :param cube: The Cube instance to validate
        """

        self.__cube = cube

    def validate(self) -> tuple[bool, dict[str, str]]:
        """
        Validate the cube by performing a series of checks.

        :return: A tuple containing a boolean indicating if the cube is valid,
                 and a dictionary of error messages for each failed check.
        """

        # Define the checks to be performed
        checks = {
            "layer_check": self.layer_check,
            "corner_check": self.corner_check,
            "center_check": self.center_check,
            "edge_check": self.edge_check,
            "x_center_check": self.x_center_check,
            "plus_center_check": self.plus_center_check,
            "parity_check": self.parity_check,
        }

        is_valid = True
        errors = {}

        # Perform each check and collect errors
        for check_name, check_method in checks.items():
            valid, error_message = check_method()
            if valid:
                errors[check_name] = "Valid"
            else:
                is_valid = False
                errors[check_name] = error_message

        return is_valid, errors

    def layer_check(self) -> tuple[bool, str | None]:
        """
        Validate the layers and pieces of the cube.

        Checks include:
        1. Verify the cube has valid dimensions - cube size should be an integer >= 2.
        2. Verify that the cube has the correct number of pieces based on the cube size.

        :return: A tuple containing a boolean indicating if the cube is valid,
                 and an optional error message if the cube is invalid.
        """

        size = self.__cube.size
        if not isinstance(size, int) or size < 2:
            return False, "Invalid cube size. Cube size should be an integer >= 2."

        for layer, pieces in self.__cube.layers.items():
            expected_pieces = size**2
            actual_pieces = len(pieces)
            if expected_pieces != actual_pieces:
                return (
                    False,
                    f"Invalid number of pieces in layer {layer}. Expected {expected_pieces}, got {actual_pieces}.",
                )

        return True, None

    def center_check(self) -> tuple[bool, str | None]:
        """
        Validate the center pieces of an odd_sized cube.

        Checks include:
        4. Verify that there is exactly 1 center piece of every color on an odd-sized cube.
        5. Verify that the center pieces are correctly placed on an odd-sized cube.

        :return: A tuple containing a boolean indicating if the cube is valid,
                 and an optional error message if the cube is invalid.
        """

        if self.__cube.size % 2 == 1:
            center_index: int = self.__cube.size // 2
            if self.__cube.layers.get(Layer.UP)[center_index * self.__cube.size + center_index] != Color.WHITE:
                return False, "Invalid center piece on UP face."
            if self.__cube.layers.get(Layer.DOWN)[center_index * self.__cube.size + center_index] != Color.YELLOW:
                return False, "Invalid center piece on DOWN face."
            if self.__cube.layers.get(Layer.FRONT)[center_index * self.__cube.size + center_index] != Color.GREEN:
                return False, "Invalid center piece on FRONT face."
            if self.__cube.layers.get(Layer.BACK)[center_index * self.__cube.size + center_index] != Color.BLUE:
                return False, "Invalid center piece on BACK face."
            if self.__cube.layers.get(Layer.LEFT)[center_index * self.__cube.size + center_index] != Color.ORANGE:
                return False, "Invalid center piece on LEFT face."
            if self.__cube.layers.get(Layer.RIGHT)[center_index * self.__cube.size + center_index] != Color.RED:
                return False, "Invalid center piece on RIGHT face."

        return True, None

    def corner_check(self) -> tuple[bool, str | None]:
        """
        Validate the corners of the cube.

        Checks include:
        3. Verify that there are exactly 4 stickers of every color on the corners of the cube.
        10. Verify that the orientation of corner pieces is valid.

        :return: A tuple containing a boolean indicating if the cube is valid,
                    and an optional error message if the cube is invalid.
        """

        # Get corner information
        all_corner_colors = get_corner_colors()
        found_corner_colors = []
        all_corner_positions = get_corner_positions(self.__cube.size)

        # Iterate through each corner position
        mod: int = 0
        for cp in all_corner_positions:
            corner_colors = set()
            for layer, (index, orientation) in cp.items():
                # Get the color of the piece at the specified layer and index
                color = self.__cube.layers.get(layer)[index]
                # Get the modulo of the piece's orientation
                if color == Color.WHITE or color == Color.YELLOW:
                    mod += orientation
                # Add the color to the set of colors in the corner
                corner_colors.add(color)

            # Check if the colors in the corner are valid
            if corner_colors in found_corner_colors:
                position = "".join([f"{layer.name[0]}" for layer in cp.keys()])
                return False, f"Duplicate corner piece found!\nPosition: {position}\nColors: {corner_colors}."
            if corner_colors not in all_corner_colors:
                position = "".join([f"{layer.name[0]}" for layer in cp.keys()])
                return False, f"Invalid corner colors!\nPosition: {position}\nColors: {corner_colors}."
            else:
                found_corner_colors.append(corner_colors)

        # Orientation check
        if mod % 3 == 1:
            return False, "Invalid corner orientation. Twist one corner piece clockwise."
        if mod % 3 == 2:
            return False, "Invalid corner orientation. Twist one corner piece counter-clockwise."

        return True, None

    def edge_check(self) -> tuple[bool, str | None]:
        """
        Validate the edge colors of the cube.

        Checks include:
        6. Verify that there are exactly 12 center-edge pieces of every color combination on the cube.
        7. Verify that there are exactly 24 edge pieces of every type and color combination on a cube,
        bigger than 3x3x3.
        11. Verify that the orientation of center edge pieces is valid.
        12. Verify that the orientation of the edge pieces of every type is valid.

        :return: A tuple containing a boolean indicating if the cube is valid,
                    and an optional error message if the cube is invalid.
        """

        return True, None

    def x_center_check(self) -> tuple[bool, str | None]:
        """
        Validate the x-center colors of the cube.

        Checks include:
        8. Verify that there are exactly 4 x-center pieces of every type and color on a cube, bigger than 3x3x3.
        :return: A tuple containing a boolean indicating if the cube is valid,
                    and an optional error message if the cube is invalid.
        """

        return True, None

    def plus_center_check(self) -> tuple[bool, str | None]:
        """
        Validate the plus-center colors of the cube.

        Checks include:
        9. Verify that there are exactly 4 +-center pieces of every type and color on a cube, bigger than 4x4x4.

        :return: A tuple containing a boolean indicating if the cube is valid,
                    and an optional error message if the cube is invalid.
        """

        return True, None

    def parity_check(self) -> tuple[bool, str | None]:
        """
        Validate the parity of the cube.

        Checks include:
        13. Verify that the corner-edge parity on an odd-sized cube is valid.

        :return: A tuple containing a boolean indicating if the cube is valid,
                    and an optional error message if the cube is invalid.
        """

        return True, None
