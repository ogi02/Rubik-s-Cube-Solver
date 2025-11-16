# Python imports
import pytest
import textwrap

from typing import Any

# Project imports
from rubik_cube_solver.cube import Cube


# fmt: off
@pytest.mark.parametrize(
    "cube_generator, expected_string", [
        (
            "solved_3x3_cube",
            """
                  W W W
                  W W W
                  W W W
            O O O G G G R R R B B B
            O O O G G G R R R B B B
            O O O G G G R R R B B B
                  Y Y Y
                  Y Y Y
                  Y Y Y
            """
        ),
        (
            "scrambled_3x3_cube",
            """
                  Y W W
                  Y W O
                  Y Y O
            B O B R B W B G R B R O
            B O O W G G R R B W B R
            O Y G O O G W Y Y G G Y
                  W B R
                  G Y R
                  G W R
            """
        ),
        (
            "solved_4x4_cube",
            """
                    W W W W
                    W W W W
                    W W W W
                    W W W W
            O O O O G G G G R R R R B B B B
            O O O O G G G G R R R R B B B B
            O O O O G G G G R R R R B B B B
            O O O O G G G G R R R R B B B B
                    Y Y Y Y
                    Y Y Y Y
                    Y Y Y Y
                    Y Y Y Y
            """
        ),
        (
            "scrambled_4x4_cube",
            """
                    G O B Y
                    R Y W R
                    B G O R
                    R G O Y
            O B Y G Y W Y G O W B O B W B W
            Y B W Y O Y W B O G Y G O G B R
            O R R W R W G G O R O R Y O B W
            W Y Y W O O G Y R B G R W G B G
                    B W W B
                    G B R Y
                    G Y O R
                    R W R B
            """
        ),
        (
            "solved_5x5_cube",
            """
                      W W W W W
                      W W W W W
                      W W W W W
                      W W W W W
                      W W W W W
            O O O O O G G G G G R R R R R B B B B B
            O O O O O G G G G G R R R R R B B B B B
            O O O O O G G G G G R R R R R B B B B B
            O O O O O G G G G G R R R R R B B B B B
            O O O O O G G G G G R R R R R B B B B B
                      Y Y Y Y Y
                      Y Y Y Y Y
                      Y Y Y Y Y
                      Y Y Y Y Y
                      Y Y Y Y Y
            """
        ),
        (
            "scrambled_5x5_cube",
            """
                      G G O O B
                      W R O Y W
                      O G W W G
                      R R R W W
                      B O W R Y
            O O B W R Y G O G G O B W R O G Y G W W
            G B G O G Y Y W W Y R W W O Y G G R B O
            R G O Y Y B R G O R G O R B R Y Y B G B
            W G R Y B Y O B B O W B B R Y R O W G B
            G R W O Y G Y Y G B R B W O Y B G G B R
                      R B O R W
                      Y G Y R R
                      B O Y Y R
                      B W B Y B
                      W O Y W O
            """
        )
    ]
)
# fmt: on
def test_cube_str_success(cube_generator: str, expected_string: str, request: pytest.FixtureRequest) -> None:
    """
    Test the string representation of the Cube class.

    :param expected_string: The expected string representation of the Cube
    """

    # Generate the cube
    cube: Cube = request.getfixturevalue(cube_generator)

    # Call the __str__ method
    actual: str = str(cube).strip()
    expected: str = textwrap.dedent(expected_string).strip()

    # Assert
    assert actual == expected


# fmt: off
@pytest.mark.parametrize(
    "cube_generator, expected_dimensions, expected_state", [
        (
            "solved_3x3_cube",
            3,
            {
                "UP": ["W"] * 9,
                "DOWN": ["Y"] * 9,
                "LEFT": ["O"] * 9,
                "RIGHT": ["R"] * 9,
                "FRONT": ["G"] * 9,
                "BACK": ["B"] * 9,
            }
        ),
        (
            "scrambled_3x3_cube",
            3,
            {
                "UP": [
                    "Y", "W", "W",
                    "Y", "W", "O",
                    "Y", "Y", "O"
                ],
                "DOWN": [
                    "W", "B", "R",
                    "G", "Y", "R",
                    "G", "W", "R"
                ],
                "LEFT": [
                    "B", "O", "B",
                    "B", "O", "O",
                    "O", "Y", "G"
                ],
                "RIGHT": [
                    "B", "G", "R",
                    "R", "R", "B",
                    "W", "Y", "Y"
                ],
                "FRONT": [
                    "R", "B", "W",
                    "W", "G", "G",
                    "O", "O", "G"
                ],
                "BACK": [
                    "B", "R", "O",
                    "W", "B", "R",
                    "G", "G", "Y"
                ],
            }
        ),
        (
            "solved_4x4_cube",
            4,
            {
                "UP": ["W"] * 16,
                "DOWN": ["Y"] * 16,
                "LEFT": ["O"] * 16,
                "RIGHT": ["R"] * 16,
                "FRONT": ["G"] * 16,
                "BACK": ["B"] * 16,
            }
        ),
        (
            "scrambled_4x4_cube",
            4,
            {
                "UP": [
                    "G", "O", "B", "Y",
                    "R", "Y", "W", "R",
                    "B", "G", "O", "R",
                    "R", "G", "O", "Y"
                ],
                "DOWN": [
                    "B", "W", "W", "B",
                    "G", "B", "R", "Y",
                    "G", "Y", "O", "R",
                    "R", "W", "R", "B"
                ],
                "LEFT": [
                    "O", "B", "Y", "G",
                    "Y", "B", "W", "Y",
                    "O", "R", "R", "W",
                    "W", "Y", "Y", "W"
                ],
                "RIGHT": [
                    "O", "W", "B", "O",
                    "O", "G", "Y", "G",
                    "O", "R", "O", "R",
                    "R", "B", "G", "R"
                ],
                "FRONT": [
                    "Y", "W", "Y", "G",
                    "O", "Y", "W", "B",
                    "R", "W", "G", "G",
                    "O", "O", "G", "Y"
                ],
                "BACK": [
                    "B", "W", "B", "W",
                    "O", "G", "B", "R",
                    "Y", "O", "B", "W",
                    "W", "G", "B", "G"
                ],
            }
        ),
        (
            "solved_5x5_cube",
            5,
            {
                "UP": ["W"] * 25,
                "DOWN": ["Y"] * 25,
                "LEFT": ["O"] * 25,
                "RIGHT": ["R"] * 25,
                "FRONT": ["G"] * 25,
                "BACK": ["B"] * 25,
            }
        ),
        (
            "scrambled_5x5_cube",
            5,
            {
                "UP": [
                    "G", "G", "O", "O", "B",
                    "W", "R", "O", "Y", "W",
                    "O", "G", "W", "W", "G",
                    "R", "R", "R", "W", "W",
                    "B", "O", "W", "R", "Y"
                ],
                "DOWN": [
                    "R", "B", "O", "R", "W",
                    "Y", "G", "Y", "R", "R",
                    "B", "O", "Y", "Y", "R",
                    "B", "W", "B", "Y", "B",
                    "W", "O", "Y", "W", "O"
                ],
                "LEFT": [
                    "O", "O", "B", "W", "R",
                    "G", "B", "G", "O", "G",
                    "R", "G", "O", "Y", "Y",
                    "W", "G", "R", "Y", "B",
                    "G", "R", "W", "O", "Y"
                ],
                "RIGHT": [
                    "O", "B", "W", "R", "O",
                    "R", "W", "W", "O", "Y",
                    "G", "O", "R", "B", "R",
                    "W", "B", "B", "R", "Y",
                    "R", "B", "W", "O", "Y"
                ],
                "FRONT": [
                    "Y", "G", "O", "G", "G",
                    "Y", "Y", "W", "W", "Y",
                    "B", "R", "G", "O", "R",
                    "Y", "O", "B", "B", "O",
                    "G", "Y", "Y", "G", "B"
                ],
                "BACK": [
                    "G", "Y", "G", "W", "W",
                    "G", "G", "R", "B", "O",
                    "Y", "Y", "B", "G", "B",
                    "R", "O", "W", "G", "B",
                    "B", "G", "G", "B", "R"
                ],
            }
        ),
    ]
)
# fmt: on
def test_cube_state_success(
        cube_generator: str, expected_dimensions: int, expected_state: dict[str, list[str]], request: pytest.FixtureRequest
) -> None:
    """
    Test the state representation of the Cube class.

    :param cube_generator: The name of the cube fixture to generate
    :param expected_dimensions: The expected dimensions of the Cube
    :param expected_state: The expected state representation of the Cube
    """

    # Generate the cube
    cube: Cube = request.getfixturevalue(cube_generator)

    # Call the state property
    state: dict[str, Any] = cube.state()
    actual_dimensions: int = state.get("dimensions")
    actual_state: dict[str, list[str]] = state.get("state")

    # Assert
    assert actual_dimensions == expected_dimensions
    assert actual_state == expected_state
