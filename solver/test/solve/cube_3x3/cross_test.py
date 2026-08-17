# Python imports
from typing import Callable

import pytest

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.cube_rotation.rotator import Rotator
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.EdgeSlot import EdgeSlot
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.solve.cube_3x3.cross import (
    CROSS_ALIGNMENT_TABLE,
    CROSS_EXTRACTION_TABLE,
    CROSS_INSERTION_TABLE,
    CROSS_ORIENTATION_TABLE,
    face_center_color,
    find_yellow_center_layer,
)
from rubik_cube_solver.solve.edge_search import search_edge

# The algorithm that, applied to a solved cube (yellow center on DOWN), moves the yellow center
# onto the given layer instead. Each entry is the inverse of the matching CROSS_ORIENTATION_TABLE
# algorithm, so applying CROSS_ORIENTATION_TABLE[layer] afterwards brings the yellow center back to
# DOWN, which is exactly the contract under test.
SETUP_ALGORITHM_FOR_YELLOW_ON: dict[Layer, str] = {
    Layer.DOWN: "",
    Layer.UP: "x2",
    Layer.FRONT: "x",
    Layer.BACK: "x'",
    Layer.LEFT: "z",
    Layer.RIGHT: "z'",
}

# The two-color identity of the cross edge that lives at each DOWN-layer slot on a solved cube.
DOWN_HOME_EDGES: dict[EdgeSlot, tuple[Color, Color]] = {
    EdgeSlot.DF: (Color.YELLOW, Color.GREEN),
    EdgeSlot.DR: (Color.YELLOW, Color.RED),
    EdgeSlot.DL: (Color.YELLOW, Color.ORANGE),
    EdgeSlot.DB: (Color.YELLOW, Color.BLUE),
}

# The two flat-list positions that make up each equatorial edge slot, empirically confirmed
# against Cube.__str__ and Rotator turns (see rubik_cube_solver.validator.validator_utils.get_edges,
# which the Cube layout already encodes the same way).
EQUATORIAL_SLOT_STICKERS: dict[EdgeSlot, tuple[Layer, int, Layer, int]] = {
    EdgeSlot.FR: (Layer.FRONT, 5, Layer.RIGHT, 3),
    EdgeSlot.FL: (Layer.FRONT, 3, Layer.LEFT, 5),
    EdgeSlot.BR: (Layer.BACK, 3, Layer.RIGHT, 5),
    EdgeSlot.BL: (Layer.BACK, 5, Layer.LEFT, 3),
}

# The UP-layer flat-list slots, used to assert an extracted piece really left the DOWN layer.
UP_LAYER_SLOTS: frozenset[EdgeSlot] = frozenset({EdgeSlot.UF, EdgeSlot.UB, EdgeSlot.UL, EdgeSlot.UR})


def _down_layer_snapshot(cube: Cube) -> tuple[Color, ...]:
    """
    Reads the raw stickers that identify the state of the DOWN-layer cross, independent of edge
    search: the four DOWN face edge stickers, and the sticker each side face shows adjacent to
    DOWN (flat-list index 7 on a 3x3 face, confirmed empirically with a D turn on a solved cube).

    :param cube: The Cube instance to read
    :return: A tuple of the 8 stickers that describe the DOWN-layer cross state
    """

    down = cube.layers[Layer.DOWN]
    return (
        down[1],
        down[3],
        down[5],
        down[7],
        cube.layers[Layer.FRONT][7],
        cube.layers[Layer.RIGHT][7],
        cube.layers[Layer.BACK][7],
        cube.layers[Layer.LEFT][7],
    )


class TestFaceCenterColor:
    # fmt: off
    @pytest.mark.parametrize(
        "cube_size, layer, expected_color", [
            (3, Layer.UP,    Color.WHITE),
            (3, Layer.DOWN,  Color.YELLOW),
            (3, Layer.LEFT,  Color.ORANGE),
            (3, Layer.RIGHT, Color.RED),
            (3, Layer.FRONT, Color.GREEN),
            (3, Layer.BACK,  Color.BLUE),
            # A larger odd cube proves the middle-index math, not just the 3x3 special case
            (5, Layer.UP,    Color.WHITE),
            (5, Layer.DOWN,  Color.YELLOW),
        ]
    )
    # fmt: on
    def test_success(
        self,
        generate_cube: Callable[[int, str], Cube],
        cube_size: int,
        layer: Layer,
        expected_color: Color,
    ) -> None:
        """
        Tests that the center sticker color is read correctly for every face of a solved cube, at
        both the standard 3x3 size and a larger odd size.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param cube_size: The cube size
        :param layer: The face to read the center sticker of
        :param expected_color: The expected center sticker color
        :return: None
        """

        # Generate the cube
        cube = generate_cube(cube_size, "")

        # Assert
        assert face_center_color(cube, layer) == expected_color


class TestFindYellowCenterLayer:
    # fmt: off
    @pytest.mark.parametrize(
        "layer", [
            Layer.DOWN,
            Layer.UP,
            Layer.FRONT,
            Layer.BACK,
            Layer.LEFT,
            Layer.RIGHT,
        ]
    )
    # fmt: on
    def test_success(self, generate_cube: Callable[[int, str], Cube], layer: Layer) -> None:
        """
        Tests that the face with the yellow center sticker is found correctly, for a cube
        reoriented by each of the six possible whole-cube rotations.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param layer: The layer the yellow center is reoriented onto
        :return: None
        """

        # Generate the cube reoriented so its yellow center sits on the given layer
        cube = generate_cube(3, SETUP_ALGORITHM_FOR_YELLOW_ON[layer])

        # Assert
        assert find_yellow_center_layer(cube) == layer

    def test_no_yellow_center(self) -> None:
        """
        Tests that searching a cube with no yellow center sticker raises a ValueError.

        :return: None
        """

        # Build a cube with all stickers white, so no face has a yellow center
        cube = Cube(3, {layer: [Color.WHITE] * 9 for layer in Layer})

        # Assert
        with pytest.raises(ValueError, match="No face has a yellow center sticker."):
            find_yellow_center_layer(cube)


class TestOrientationTable:
    # fmt: off
    @pytest.mark.parametrize(
        "layer", [
            Layer.DOWN,
            Layer.UP,
            Layer.FRONT,
            Layer.BACK,
            Layer.LEFT,
            Layer.RIGHT,
        ]
    )
    # fmt: on
    def test_brings_yellow_center_to_down(self, generate_cube: Callable[[int, str], Cube], layer: Layer) -> None:
        """
        Tests that every CROSS_ORIENTATION_TABLE entry really brings the yellow center from its face to
        DOWN, verified against the real Rotator.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param layer: The face the yellow center starts on
        :return: None
        """

        # Generate the cube reoriented so its yellow center sits on the given layer
        cube = generate_cube(3, SETUP_ALGORITHM_FOR_YELLOW_ON[layer])
        assert face_center_color(cube, layer) == Color.YELLOW
        rotator = Rotator(cube)

        # Apply the orientation algorithm
        rotator.apply(Algorithm.from_str(CROSS_ORIENTATION_TABLE[layer]))

        # Assert
        assert face_center_color(cube, Layer.DOWN) == Color.YELLOW


class TestExtractionTable:
    # fmt: off
    @pytest.mark.parametrize(
        "slot", [
            EdgeSlot.DF,
            EdgeSlot.DR,
            EdgeSlot.DL,
            EdgeSlot.DB,
        ]
    )
    # fmt: on
    def test_down_layer_slot(self, generate_cube: Callable[[int, str], Cube], slot: EdgeSlot) -> None:
        """
        Tests that every DOWN-layer CROSS_EXTRACTION_TABLE entry moves the piece out of that slot into
        the UP layer and leaves the other three DOWN-layer edges in place, verified against the
        real Rotator.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param slot: The DOWN-layer slot under test
        :return: None
        """

        # Generate a solved cube, whose cross is already complete
        cube = generate_cube(3, "")
        rotator = Rotator(cube)
        other_slots = [other for other in DOWN_HOME_EDGES if other is not slot]
        other_pieces_before = [search_edge(cube, *DOWN_HOME_EDGES[other]) for other in other_slots]

        # Extract the piece
        rotator.apply(Algorithm.from_str(CROSS_EXTRACTION_TABLE[slot]))

        # Assert the piece moved into the UP layer
        moved_slot, _ = search_edge(cube, *DOWN_HOME_EDGES[slot])
        assert moved_slot in UP_LAYER_SLOTS

        # Assert the other three DOWN-layer edges are untouched
        other_pieces_after = [search_edge(cube, *DOWN_HOME_EDGES[other]) for other in other_slots]
        assert other_pieces_after == other_pieces_before

    # fmt: off
    @pytest.mark.parametrize(
        "slot", [
            EdgeSlot.FR,
            EdgeSlot.FL,
            EdgeSlot.BR,
            EdgeSlot.BL,
        ]
    )
    # fmt: on
    def test_equatorial_slot(self, generate_cube: Callable[[int, str], Cube], slot: EdgeSlot) -> None:
        """
        Tests that every equatorial CROSS_EXTRACTION_TABLE entry moves the piece out of that slot into
        the UP layer and leaves the DOWN-layer cross untouched, verified against the real Rotator.

        A yellow-green cross edge is hand-placed at the equatorial slot under test, since a solved
        cube has no cross edge sitting there, and the solved cube's own yellow-green piece is first
        cleared out of DF so the searched piece can only be the one under test.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param slot: The equatorial slot under test
        :return: None
        """

        # Generate a solved cube, clear DF and place a yellow-green edge at the slot under test
        cube = generate_cube(3, "")
        cube.layers[Layer.DOWN][1] = Color.WHITE
        cube.layers[Layer.FRONT][7] = Color.RED
        first_layer, first_index, second_layer, second_index = EQUATORIAL_SLOT_STICKERS[slot]
        cube.layers[first_layer][first_index] = Color.YELLOW
        cube.layers[second_layer][second_index] = Color.GREEN
        assert search_edge(cube, Color.YELLOW, Color.GREEN).slot is slot
        rotator = Rotator(cube)
        down_layer_before = _down_layer_snapshot(cube)

        # Extract the piece
        rotator.apply(Algorithm.from_str(CROSS_EXTRACTION_TABLE[slot]))

        # Assert the piece moved into the UP layer
        moved_slot, _ = search_edge(cube, Color.YELLOW, Color.GREEN)
        assert moved_slot in UP_LAYER_SLOTS

        # Assert the DOWN-layer cross is untouched
        assert _down_layer_snapshot(cube) == down_layer_before


class TestAlignmentTable:
    # The algorithm that, applied to a solved cube, moves the UF cross edge to the slot under
    # test, so CROSS_ALIGNMENT_TABLE can be exercised on it from there.
    # fmt: off
    _SETUP_ALGORITHM: dict[EdgeSlot, str] = {
        EdgeSlot.UF: "",
        EdgeSlot.UR: "U'",
        EdgeSlot.UB: "U2",
        EdgeSlot.UL: "U",
    }

    @pytest.mark.parametrize(
        "slot", [
            EdgeSlot.UF,
            EdgeSlot.UR,
            EdgeSlot.UB,
            EdgeSlot.UL,
        ]
    )
    # fmt: on
    def test_brings_piece_to_uf(self, generate_cube: Callable[[int, str], Cube], slot: EdgeSlot) -> None:
        """
        Tests that every CROSS_ALIGNMENT_TABLE entry really brings a UP-layer piece to UF, verified
        against the real Rotator.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param slot: The UP-layer slot under test
        :return: None
        """

        # Generate a cube with the white-green edge moved to the slot under test
        cube = generate_cube(3, self._SETUP_ALGORITHM[slot])
        assert search_edge(cube, Color.WHITE, Color.GREEN) == (slot, True)
        rotator = Rotator(cube)

        # Align the piece
        rotator.apply(Algorithm.from_str(CROSS_ALIGNMENT_TABLE[slot]))

        # Assert
        assert search_edge(cube, Color.WHITE, Color.GREEN) == (EdgeSlot.UF, True)


class TestInsertionTable:
    # fmt: off
    @pytest.mark.parametrize(
        "is_good", [
            True,
            False,
        ]
    )
    # fmt: on
    def test_inserts_piece_at_df(self, generate_cube: Callable[[int, str], Cube], is_good: bool) -> None:
        """
        Tests that both CROSS_INSERTION_TABLE entries really place a UF piece at DF with yellow on DOWN
        and the side color on FRONT, verified against the real Rotator.

        The DF slot is first cleared of its own solved yellow-green piece so it cannot be confused
        with the piece under test once it arrives.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param is_good: Whether the piece placed at UF is already oriented (yellow on UP)
        :return: None
        """

        # Generate a solved cube and clear DF, then place a yellow-green edge at UF
        cube = generate_cube(3, "")
        cube.layers[Layer.DOWN][1] = Color.WHITE
        cube.layers[Layer.FRONT][7] = Color.RED
        if is_good:
            cube.layers[Layer.UP][7] = Color.YELLOW
            cube.layers[Layer.FRONT][1] = Color.GREEN
        else:
            cube.layers[Layer.UP][7] = Color.GREEN
            cube.layers[Layer.FRONT][1] = Color.YELLOW
        rotator = Rotator(cube)

        # Insert the piece
        rotator.apply(Algorithm.from_str(CROSS_INSERTION_TABLE[is_good]))

        # Assert the piece is at DF, yellow on DOWN and the side color on FRONT
        assert cube.layers[Layer.DOWN][1] == Color.YELLOW
        assert cube.layers[Layer.FRONT][7] == Color.GREEN
