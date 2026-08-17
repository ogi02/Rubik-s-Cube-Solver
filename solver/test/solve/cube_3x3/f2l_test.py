# Python imports
from typing import Callable

import pytest

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.cube_rotation.rotator import Rotator
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.CornerSlot import CornerSlot
from rubik_cube_solver.enums.EdgeSlot import EdgeSlot
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.solve.corner_search import search_corner
from rubik_cube_solver.solve.cube_3x3.f2l import (
    F2L_CORNER_ALIGNMENT_TABLE,
    F2L_CORNER_EXTRACTION_TABLE,
    F2L_EDGE_EXTRACTION_TABLE,
    F2L_PAIR_INSERTION_TABLE,
    front_color_on_up,
    is_pair_solved,
)
from rubik_cube_solver.solve.edge_search import search_edge

# The three-color identity of the corner that lives at each DOWN-layer slot on a solved cube.
DOWN_HOME_CORNERS: dict[CornerSlot, tuple[Color, Color, Color]] = {
    CornerSlot.DFR: (Color.YELLOW, Color.GREEN, Color.RED),
    CornerSlot.DFL: (Color.YELLOW, Color.ORANGE, Color.GREEN),
    CornerSlot.DBR: (Color.YELLOW, Color.RED, Color.BLUE),
    CornerSlot.DBL: (Color.YELLOW, Color.BLUE, Color.ORANGE),
}

# The two-color identity of the edge that lives at each DOWN-layer slot on a solved cube.
DOWN_HOME_EDGES: dict[EdgeSlot, tuple[Color, Color]] = {
    EdgeSlot.DF: (Color.YELLOW, Color.GREEN),
    EdgeSlot.DR: (Color.YELLOW, Color.RED),
    EdgeSlot.DL: (Color.YELLOW, Color.ORANGE),
    EdgeSlot.DB: (Color.YELLOW, Color.BLUE),
}

# The two-color identity of the edge that lives at each equatorial slot on a solved cube.
EQUATORIAL_HOME_EDGES: dict[EdgeSlot, tuple[Color, Color]] = {
    EdgeSlot.FR: (Color.GREEN, Color.RED),
    EdgeSlot.FL: (Color.GREEN, Color.ORANGE),
    EdgeSlot.BR: (Color.BLUE, Color.RED),
    EdgeSlot.BL: (Color.BLUE, Color.ORANGE),
}

# The equatorial edge slot belonging to the same F2L pair as each DOWN-layer corner slot.
PAIR_SLOTS: dict[CornerSlot, EdgeSlot] = {
    CornerSlot.DFR: EdgeSlot.FR,
    CornerSlot.DFL: EdgeSlot.FL,
    CornerSlot.DBR: EdgeSlot.BR,
    CornerSlot.DBL: EdgeSlot.BL,
}

# The UP-layer slots, used to assert an extracted piece really reached the UP layer.
UP_CORNER_SLOTS: frozenset[CornerSlot] = frozenset({CornerSlot.UFL, CornerSlot.UFR, CornerSlot.UBL, CornerSlot.UBR})
UP_EDGE_SLOTS: frozenset[EdgeSlot] = frozenset({EdgeSlot.UF, EdgeSlot.UB, EdgeSlot.UL, EdgeSlot.UR})

# The flat-list positions of the front-right pair on a 3x3: the three stickers of the DFR corner
# and the two of the FR edge, hand-verified against Cube.__str__ and a D turn on a solved cube.
PAIR_STICKERS: tuple[tuple[Layer, int, Color], ...] = (
    (Layer.DOWN, 2, Color.YELLOW),
    (Layer.FRONT, 8, Color.GREEN),
    (Layer.RIGHT, 6, Color.RED),
    (Layer.FRONT, 5, Color.GREEN),
    (Layer.RIGHT, 3, Color.RED),
)


def _first_two_layers_pieces(cube: Cube, excluded: CornerSlot) -> list[tuple]:
    """
    Searches every piece of the first two layers except the pair of the excluded corner slot.

    An extraction algorithm is allowed to disturb the pair it lifts out and the UP layer, and
    nothing else - so comparing this list before and after is what pins that property down.

    :param cube: The Cube instance to search
    :param excluded: The corner slot whose pair the algorithm under test is allowed to disturb
    :return: The search result of every other DOWN-layer and equatorial piece
    """

    corners = [search_corner(cube, *colors) for slot, colors in DOWN_HOME_CORNERS.items() if slot is not excluded]
    equatorial = [
        search_edge(cube, *colors) for slot, colors in EQUATORIAL_HOME_EDGES.items() if slot is not PAIR_SLOTS[excluded]
    ]
    cross = [search_edge(cube, *colors) for colors in DOWN_HOME_EDGES.values()]
    return corners + equatorial + cross


class TestFrontColorOnUp:
    # fmt: off
    @pytest.mark.parametrize(
        "slot, sticker_index", [
            (EdgeSlot.UF, 7),
            (EdgeSlot.UR, 5),
            (EdgeSlot.UB, 1),
            (EdgeSlot.UL, 3),
        ]
    )
    @pytest.mark.parametrize(
        "up_color, expected", [
            (Color.GREEN, True),
            (Color.RED,   False),
        ]
    )
    # fmt: on
    def test_success(
        self,
        generate_cube: Callable[[int, str], Cube],
        slot: EdgeSlot,
        sticker_index: int,
        up_color: Color,
        expected: bool,
    ) -> None:
        """
        Tests that the FRONT color is recognized on the UP sticker of each UP-layer edge slot. The
        cube is solved, so the FRONT center is green and the RIGHT center is red.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param slot: The UP-layer slot under test
        :param sticker_index: The flat-list index of that slot's sticker on the UP face
        :param up_color: The color placed on the UP sticker
        :param expected: Whether that color is the FRONT center's color
        :return: None
        """

        # Generate a solved cube and paint the UP sticker of the slot under test
        cube = generate_cube(3, "")
        cube.layers[Layer.UP][sticker_index] = up_color

        # Assert
        assert front_color_on_up(cube, slot) is expected


class TestIsPairSolved:
    # fmt: off
    @pytest.mark.parametrize(
        "algorithm, expected", [
            ("",          True),
            ("U",         True),
            ("U2 R2 U2",  False),
            ("R",         False),
            ("D",         False),
            ("R U R' U'", False),
        ]
    )
    # fmt: on
    def test_success(self, generate_cube: Callable[[int, str], Cube], algorithm: str, expected: bool) -> None:
        """
        Tests that the front-right pair is reported as solved only while both of its pieces sit in
        the slot. A U turn leaves the slot alone, while the other algorithms move a piece out of it.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param algorithm: The algorithm applied before the check
        :param expected: Whether the pair is still solved afterwards
        :return: None
        """

        # Generate the cube
        cube = generate_cube(3, algorithm)

        # Assert
        assert is_pair_solved(cube, Color.GREEN, Color.RED) is expected

    def test_edge_flipped_in_slot(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that an edge sitting in FR the wrong way round does not count as solved. The flag of
        `search_edge` cannot see this, so it is the sticker read that has to catch it.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate a solved cube and flip the FR edge in place
        cube = generate_cube(3, "")
        cube.layers[Layer.FRONT][5] = Color.RED
        cube.layers[Layer.RIGHT][3] = Color.GREEN

        # Assert
        assert is_pair_solved(cube, Color.GREEN, Color.RED) is False

    def test_corner_twisted_in_slot(self, generate_cube: Callable[[int, str], Cube]) -> None:
        """
        Tests that a corner sitting in DFR twisted does not count as solved.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :return: None
        """

        # Generate a solved cube and twist the DFR corner in place
        cube = generate_cube(3, "")
        cube.layers[Layer.DOWN][2] = Color.RED
        cube.layers[Layer.FRONT][8] = Color.YELLOW
        cube.layers[Layer.RIGHT][6] = Color.GREEN

        # Assert
        assert is_pair_solved(cube, Color.GREEN, Color.RED) is False


class TestCornerExtractionTable:
    # fmt: off
    @pytest.mark.parametrize(
        "slot", [
            CornerSlot.DFR,
            CornerSlot.DFL,
            CornerSlot.DBR,
            CornerSlot.DBL,
        ]
    )
    # fmt: on
    def test_lifts_corner_into_up_layer(self, generate_cube: Callable[[int, str], Cube], slot: CornerSlot) -> None:
        """
        Tests that every F2L_CORNER_EXTRACTION_TABLE entry lifts the corner out of that DOWN-layer slot
        into the UP layer and leaves every first-two-layers piece outside that pair where it was,
        verified against the real Rotator.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param slot: The DOWN-layer corner slot under test
        :return: None
        """

        # Generate a solved cube, whose first two layers are complete
        cube = generate_cube(3, "")
        rotator = Rotator(cube)
        pieces_before = _first_two_layers_pieces(cube, slot)

        # Extract the corner
        rotator.apply(Algorithm.from_str(F2L_CORNER_EXTRACTION_TABLE[slot]))

        # Assert the corner moved into the UP layer
        moved_slot, _ = search_corner(cube, *DOWN_HOME_CORNERS[slot])
        assert moved_slot in UP_CORNER_SLOTS

        # Assert every piece outside that pair is untouched
        assert _first_two_layers_pieces(cube, slot) == pieces_before


class TestCornerAlignmentTable:
    # The algorithm that, applied to a solved cube, moves the white-green-red corner from UFR to
    # the slot under test, so F2L_CORNER_ALIGNMENT_TABLE can be exercised on it from there.
    # fmt: off
    _SETUP_ALGORITHM: dict[CornerSlot, str] = {
        CornerSlot.UFR: "",
        CornerSlot.UFL: "U",
        CornerSlot.UBL: "U2",
        CornerSlot.UBR: "U'",
    }

    @pytest.mark.parametrize(
        "slot", [
            CornerSlot.UFR,
            CornerSlot.UFL,
            CornerSlot.UBL,
            CornerSlot.UBR,
        ]
    )
    # fmt: on
    def test_brings_corner_to_ufr(self, generate_cube: Callable[[int, str], Cube], slot: CornerSlot) -> None:
        """
        Tests that every F2L_CORNER_ALIGNMENT_TABLE entry really brings a UP-layer corner to UFR,
        verified against the real Rotator.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param slot: The UP-layer corner slot under test
        :return: None
        """

        # Generate a cube with the white-green-red corner moved to the slot under test
        cube = generate_cube(3, self._SETUP_ALGORITHM[slot])
        assert search_corner(cube, Color.WHITE, Color.GREEN, Color.RED).slot is slot
        rotator = Rotator(cube)

        # Align the corner
        rotator.apply(Algorithm.from_str(F2L_CORNER_ALIGNMENT_TABLE[slot]))

        # Assert
        assert search_corner(cube, Color.WHITE, Color.GREEN, Color.RED).slot is CornerSlot.UFR


class TestEdgeExtractionTable:
    # fmt: off
    @pytest.mark.parametrize(
        "slot, corner_slot", [
            (EdgeSlot.FR, CornerSlot.DFR),
            (EdgeSlot.FL, CornerSlot.DFL),
            (EdgeSlot.BR, CornerSlot.DBR),
            (EdgeSlot.BL, CornerSlot.DBL),
        ]
    )
    # fmt: on
    def test_lifts_edge_into_up_layer(
        self,
        generate_cube: Callable[[int, str], Cube],
        slot: EdgeSlot,
        corner_slot: CornerSlot,
    ) -> None:
        """
        Tests that every F2L_EDGE_EXTRACTION_TABLE entry lifts the edge out of that equatorial slot into
        the UP layer, leaves a corner aligned at UFR somewhere in the UP layer, and leaves every
        first-two-layers piece outside that pair where it was, verified against the real Rotator.

        Keeping the aligned corner in the UP layer is why these entries differ from the cross's: the
        pair's corner is aligned to UFR before the edge is extracted, and the insertion that follows
        expects to find it still up there.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param slot: The equatorial edge slot under test
        :param corner_slot: The DOWN-layer corner slot of the same pair
        :return: None
        """

        # Generate a solved cube, which already has the white-green-red corner at UFR
        cube = generate_cube(3, "")
        rotator = Rotator(cube)
        pieces_before = _first_two_layers_pieces(cube, corner_slot)

        # Extract the edge
        rotator.apply(Algorithm.from_str(F2L_EDGE_EXTRACTION_TABLE[slot]))

        # Assert the edge moved into the UP layer
        moved_slot, _ = search_edge(cube, *EQUATORIAL_HOME_EDGES[slot])
        assert moved_slot in UP_EDGE_SLOTS

        # Assert the corner that was aligned at UFR is still in the UP layer
        assert search_corner(cube, Color.WHITE, Color.GREEN, Color.RED).slot in UP_CORNER_SLOTS

        # Assert every piece outside that pair is untouched
        assert _first_two_layers_pieces(cube, corner_slot) == pieces_before


class TestPairInsertionTable:
    @pytest.mark.parametrize("case, algorithm", list(F2L_PAIR_INSERTION_TABLE.items()))
    def test_inserts_pair_into_front_right_slot(
        self,
        generate_f2l_case: Callable[[str], Cube],
        case: tuple[int, EdgeSlot, bool],
        algorithm: str,
    ) -> None:
        """
        Tests every F2L_PAIR_INSERTION_TABLE entry against the real Rotator: the case it is keyed by is
        set up by applying the entry backwards to a solved cube, which is then asserted to really be
        that case before the entry is applied forwards and has to fill the front-right slot.

        Reading the case back off the cube is what makes this more than a tautology - it is the key,
        not the algorithm, that recognition has to agree with.

        :param generate_f2l_case: Fixture generating the case a given insertion algorithm solves
        :param case: The corner orientation, edge slot and edge orientation the entry is keyed by
        :param algorithm: The insertion algorithm of that entry
        :return: None
        """

        # Generate the case by applying the entry backwards to a solved cube
        orientation, edge_slot, is_front_color_on_up = case
        cube = generate_f2l_case(algorithm)
        rotator = Rotator(cube)

        # Assert the cube really is in the case the entry is keyed by
        assert search_corner(cube, Color.YELLOW, Color.GREEN, Color.RED) == (CornerSlot.UFR, orientation)
        assert search_edge(cube, Color.GREEN, Color.RED).slot is edge_slot
        assert front_color_on_up(cube, edge_slot) is is_front_color_on_up
        pieces_before = _first_two_layers_pieces(cube, CornerSlot.DFR)

        # Insert the pair
        rotator.apply(Algorithm.from_str(algorithm))

        # Assert the pair fills the front-right slot
        for layer, index, color in PAIR_STICKERS:
            assert cube.layers[layer][index] == color

        # Assert every other piece of the first two layers is untouched
        assert _first_two_layers_pieces(cube, CornerSlot.DFR) == pieces_before
