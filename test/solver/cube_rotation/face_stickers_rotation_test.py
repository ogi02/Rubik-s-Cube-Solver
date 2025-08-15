import pytest

from typing import Callable

from src.solver.enums.Color import Color
from src.solver.enums.Direction import Direction
from src.solver.cube_rotation.face_stickers_rotation import FaceRotation


# -----------------------
# Fixtures
# -----------------------
RUBIKS_CUBE_COLORS: list[Color] = [Color.WHITE, Color.YELLOW, Color.ORANGE, Color.RED, Color.GREEN, Color.BLUE]


@pytest.fixture
def rotation() -> FaceRotation:
    """
    Returns an instance of FaceRotation
    :return: FaceRotation
    """
    return FaceRotation()


@pytest.fixture
def generate_face() -> Callable[[int], list[Color]]:
    """
    Returns a function to generate an n x n face with repeating Rubik's colors.

    :return: The callable function
    """
    def _generate(n: int) -> list[Color]:
        """
        Generates an n x n face with repeating Rubik's colors.

        :param n: Cube size
        :return: Face with repeating Rubik's colors
        """
        face: list[Color] = []
        for i in range(n * n):
            face.append(RUBIKS_CUBE_COLORS[i % len(RUBIKS_CUBE_COLORS)])
        return face

    return _generate


# -----------------------
# Tests
# -----------------------
@pytest.mark.parametrize("n", [2, 3, 4, 5, 6, 7])
def test_rotate_face_round_trip(rotation: FaceRotation, generate_face: Callable[[int], list[Color]], n: int) -> None:
    """
    Tests rotation of a face with round trips.
    Parametrized for cube size from 2x2 to 7x7.

    :param rotation: The FaceRotation fixture
    :param generate_face: The callable fixture
    :param n: Cube size
    :return: None
    """
    face: list[Color] = generate_face(n)

    # Clockwise rotation
    rotated_cw: list[Color] = rotation.rotate_face(n, face, Direction.CW)
    # Counter-clockwise rotation
    rotated_ccw: list[Color] = rotation.rotate_face(n, face, Direction.CCW)
    # Double rotation
    rotated_double: list[Color] = rotation.rotate_face(n, face, Direction.DOUBLE)

    # Round-trip checks
    assert rotation.rotate_face(n, rotated_cw, Direction.CCW) == face
    assert rotation.rotate_face(n, rotated_ccw, Direction.CW) == face
    assert rotation.rotate_face(n, rotated_double, Direction.DOUBLE) == face


@pytest.mark.parametrize("direction,expected_indices", [
    (Direction.CW, [6, 3, 0, 7, 4, 1, 8, 5, 2]),
    (Direction.CCW, [2, 5, 8, 1, 4, 7, 0, 3, 6]),
    (Direction.DOUBLE, [8, 7, 6, 5, 4, 3, 2, 1, 0])
])
def test_rotate_face_3x3_exact(rotation: FaceRotation, direction: Direction, expected_indices: list[int]) -> None:
    """
    For 3x3 cube, verify that the rotation produces exactly the expected sticker positions.

    :param rotation: The FaceRotation fixture
    :param direction: The Direction fixture
    :param expected_indices: The expected sticker positions
    :return: None
    """
    # 3x3 face with unique colors for easy tracking
    face: list[Color] = [
        Color.WHITE, Color.YELLOW, Color.RED,
        Color.ORANGE, Color.GREEN, Color.BLUE,
        Color.WHITE, Color.YELLOW, Color.RED
    ]

    rotated: list[Color] = rotation.rotate_face(3, face, direction)

    # Expected face after rotation
    expected: list[Color] = [face[i] for i in expected_indices]

    assert rotated == expected
