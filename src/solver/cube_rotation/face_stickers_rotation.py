from src.solver.enums.Color import Color
from src.solver.enums.Direction import Direction


class FaceStickersRotation:
    """
    Face rotation maps and a method to rotate face.
    The rotation involves moving the colors around in the face array.
    """

    @staticmethod
    def __generate_clockwise_rotation_map(cube_size: int):
        """
        Generates the rotation map for a clockwise rotation.

        How does it work?

        The 1D representation of a stickers is: row * cube_size + col.

        When performing a clockwise turn:

            - The new row becomes the old column:
                G W W        W W G
                W W W   ->   W W W   -> Old column 0 becomes new row 0
                W W W        W W W

            - The new column becomes the mirror of the old row:
                G W W        W W G
                W W W   ->   W W W   -> Mirrored Old row 0 becomes new column 2
                W W W        W W W      (for 3x3 cube, where the possible columns are 0, 1, 2)

                W W W W        W W W W
                W G W W   ->   W W G W   -> Mirrored Old row 1 becomes new column 2
                W W W W        W W W W      (for 4x4 cube, where the possible columns are 0, 1, 2, 3)
                W W W W        W W W W

        In a 1D representation:

            - The new row is calculated the following way:

                new_row = old_column * cube_size

            - The new column is calculated the following way:

                new_column = cube_size - 1 - old_row

            - The complete calculation is:

                new_place = old_column * cube_size + (cube_size - 1 - old_row)

        Each row and column is iterated and the new place for the given sticker (row, col) is appended to the rotation map.

        :param cube_size: Cube size.
        :return: The rotation map.
        """
        rotation_map: list[int] = []
        for row in range(cube_size):
            for col in range(cube_size):
                rotation_map.append(col * cube_size + (cube_size - 1 - row))
        return rotation_map

    @staticmethod
    def __generate_counter_clockwise_rotation_map(cube_size: int):
        """
        Generates the rotation map for a counter-clockwise rotation.

        How does it work?

        The 1D representation of a stickers is: row * cube_size + col.

        When performing a counter-clockwise turn:

            - The new column becomes the old row:
                W W G        G W W
                W W W   ->   W W W   -> Old row 0 becomes new column 0
                W W W        W W W

            - The new row becomes the mirror of the old column:
                W W G        G W W
                W W W   ->   W W W   -> Mirrored Old column 2 becomes new row 0
                W W W        W W W      (for 3x3 cube, where the possible rows are 0, 1, 2)

                W W W W        W W W W
                W W G W   ->   W G W W   -> Mirrored Old column 2 becomes new row 1
                W W W W        W W W W      (for 4x4 cube, where the possible rows are 0, 1, 2, 3)
                W W W W        W W W W

        In a 1D representation:

            - The new row is calculated the following way:

                new_row = (cube_size - 1 - old_column) * cube_size

            - The new column is calculated the following way:

                new_column = old_row

            - The complete calculation is:

                new_place = (cube_size - 1 - old_column) * cube_size + old_row

        Each row and column is iterated and the new place for the given sticker (row, col) is appended to the rotation map.

        :param cube_size: Cube size
        :return: The rotation map
        """

        rotation_map: list[int] = []
        for row in range(cube_size):
            for col in range(cube_size):
                rotation_map.append((cube_size - 1 - col) * cube_size + row)
        return rotation_map

    @staticmethod
    def __generate_double_rotation_map(cube_size: int):
        """
        Generates the rotation map for a double rotation.

        How does it work?

        When performing a double turn the array of stickers reverses:

            W G W        B Y B
            R Y R   ->   R Y R
            B Y B        W G W

        :param cube_size: Cube size
        :return: The rotation map
        """

        return [i for i in range(cube_size**2 - 1, -1, -1)]

    def __generate_rotation_map(self, cube_size: int, direction: Direction):
        """
        Generates the rotation map for the given direction based on the cube size.

        :param cube_size: Cube size
        :param direction: The direction to rotate the face
        :return: The rotation map
        """

        match direction:
            case Direction.CW:
                return self.__generate_clockwise_rotation_map(cube_size)
            case Direction.CCW:
                return self.__generate_counter_clockwise_rotation_map(cube_size)
            case Direction.DOUBLE:
                return self.__generate_double_rotation_map(cube_size)
            case _:
                raise ValueError("Unexpected direction when trying to rotate face!")


    def rotate_face(self, cube_size: int, face: list[Color], direction: Direction) -> list[Color]:
        """
        Generates the rotation map for the given direction based on the cube size.
        Rotates the face based on the generated rotation map.

        :param cube_size: Cube size
        :param face: The array of colors for the face
        :param direction: The direction to rotate the face
        :return: The rotated face
        """

        # Create a template for the rotated face
        rotated_face: list[Color] = [None] * cube_size ** 2
        print(len(rotated_face))
        # Put every sticker of the map in its new position
        for new_pos, index in enumerate(self.__generate_rotation_map(cube_size, direction)):
            rotated_face[index] = face[new_pos]

        return rotated_face
