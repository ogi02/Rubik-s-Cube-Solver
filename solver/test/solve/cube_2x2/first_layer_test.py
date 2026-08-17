# Python imports
from typing import Callable

import pytest

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.cube_rotation.rotator import Rotator
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.CornerSlot import CornerSlot
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.solve.corner_search import search_corner
from rubik_cube_solver.solve.cube_2x2.first_layer import (
    FIRST_LAYER_ALIGNMENT_TABLE,
    FIRST_LAYER_CORNER_COLORS,
    FIRST_LAYER_EXTRACTION_TABLE,
    FIRST_LAYER_INSERTION_TABLE,
)

# The three flat-list stickers of every corner slot of a 2x2, in the clockwise face order the
# validator reads a corner in. Reading them directly keeps the assertions independent of
# `search_corner`, and the order makes a slot's sticker tuple say both which piece sits there and
# how it is turned.
# fmt: off
CORNER_STICKERS: dict[CornerSlot, tuple[tuple[Layer, int], ...]] = {
    CornerSlot.UFL: ((Layer.UP,   2), (Layer.FRONT, 0), (Layer.LEFT,  1)),
    CornerSlot.UFR: ((Layer.UP,   3), (Layer.RIGHT, 0), (Layer.FRONT, 1)),
    CornerSlot.UBL: ((Layer.UP,   0), (Layer.LEFT,  0), (Layer.BACK,  1)),
    CornerSlot.UBR: ((Layer.UP,   1), (Layer.BACK,  0), (Layer.RIGHT, 1)),
    CornerSlot.DFL: ((Layer.DOWN, 0), (Layer.LEFT,  3), (Layer.FRONT, 2)),
    CornerSlot.DFR: ((Layer.DOWN, 1), (Layer.FRONT, 3), (Layer.RIGHT, 2)),
    CornerSlot.DBL: ((Layer.DOWN, 2), (Layer.BACK,  3), (Layer.LEFT,  2)),
    CornerSlot.DBR: ((Layer.DOWN, 3), (Layer.RIGHT, 3), (Layer.BACK,  2)),
}
# fmt: on

# The four slots of the layer being solved, and the four the pieces are lifted into.
DOWN_SLOTS: tuple[CornerSlot, ...] = (CornerSlot.DFR, CornerSlot.DFL, CornerSlot.DBR, CornerSlot.DBL)
UP_SLOTS: tuple[CornerSlot, ...] = (CornerSlot.UFR, CornerSlot.UFL, CornerSlot.UBR, CornerSlot.UBL)

# The corner the first layer's tables are written for: the one that belongs at the front-right slot
# of a solved cube.
FRONT_RIGHT_CORNER: tuple[Color, Color, Color] = (Color.YELLOW, Color.GREEN, Color.RED)


def _corner_at(cube: Cube, slot: CornerSlot) -> tuple[Color, ...]:
    """
    Reads the three stickers of a corner slot, in the clockwise face order the validator reads a
    corner in, so two equal tuples mean the same piece turned the same way.

    :param cube: The Cube instance to read
    :param slot: The corner slot to read
    :return: The three sticker colors of the slot
    """

    return tuple(cube.layers[layer][index] for layer, index in CORNER_STICKERS[slot])


class TestFirstLayerCornerColors:
    @pytest.mark.parametrize("rotations, colors", list(enumerate(FIRST_LAYER_CORNER_COLORS)))
    def test_names_the_corner_of_the_front_right_slot(
        self,
        generate_cube: Callable[[int, str], Cube],
        rotations: int,
        colors: tuple[Color, Color],
    ) -> None:
        """
        Tests that the entries of FIRST_LAYER_CORNER_COLORS are the four DOWN corners in the order a
        `y` rotation brings them to the front-right slot: after the same number of `y` rotations as
        the entry's index, a solved cube shows exactly that corner at DFR, with the entry's two
        colors on FRONT and RIGHT.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param rotations: The number of `y` rotations, which is the entry's index
        :param colors: The FRONT and RIGHT colors of the entry
        :return: None
        """

        # Generate a solved cube rotated to the entry's position
        cube = generate_cube(2, " ".join(["y"] * rotations))

        # Assert
        assert _corner_at(cube, CornerSlot.DFR) == (Color.YELLOW, *colors)


class TestFirstLayerExtractionTable:
    @pytest.mark.parametrize("slot, algorithm", list(FIRST_LAYER_EXTRACTION_TABLE.items()))
    def test_lifts_the_corner_into_the_up_layer(
        self,
        generate_cube: Callable[[int, str], Cube],
        slot: CornerSlot,
        algorithm: str,
    ) -> None:
        """
        Tests that every extraction entry moves the corner of its slot into the UP layer and leaves
        the other three DOWN corners exactly where they were, which is what lets a corner be
        extracted without breaking the ones already solved.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param slot: The DOWN slot the entry is keyed by
        :param algorithm: The extraction algorithm of that entry
        :return: None
        """

        # Generate a solved cube and note where its DOWN corners are
        cube = generate_cube(2, "")
        extracted = _corner_at(cube, slot)
        others = {other: _corner_at(cube, other) for other in DOWN_SLOTS if other is not slot}

        # Extract the corner
        Rotator(cube).apply(Algorithm.from_str(algorithm))

        # Assert the corner reached the UP layer
        assert any(set(_corner_at(cube, up_slot)) == set(extracted) for up_slot in UP_SLOTS)

        # Assert the other DOWN corners did not move
        assert all(_corner_at(cube, other) == corner for other, corner in others.items())


class TestFirstLayerAlignmentTable:
    @pytest.mark.parametrize("slot, algorithm", list(FIRST_LAYER_ALIGNMENT_TABLE.items()))
    def test_brings_the_corner_to_ufr(
        self,
        generate_cube: Callable[[int, str], Cube],
        slot: CornerSlot,
        algorithm: str,
    ) -> None:
        """
        Tests that every alignment entry brings the corner of its UP slot to UFR, above the slot
        being solved, without turning it.

        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param slot: The UP slot the entry is keyed by
        :param algorithm: The alignment algorithm of that entry
        :return: None
        """

        # Generate a solved cube and note the corner to align
        cube = generate_cube(2, "")
        aligned = _corner_at(cube, slot)

        # Align the corner
        Rotator(cube).apply(Algorithm.from_str(algorithm))

        # Assert
        assert _corner_at(cube, CornerSlot.UFR) == aligned


class TestFirstLayerInsertionTable:
    @pytest.mark.parametrize("orientation, algorithm", list(FIRST_LAYER_INSERTION_TABLE.items()))
    def test_inserts_the_corner_into_dfr(
        self,
        generate_first_layer_case: Callable[[str], Cube],
        generate_cube: Callable[[int, str], Cube],
        orientation: int,
        algorithm: str,
    ) -> None:
        """
        Tests that every insertion entry solves the case it is keyed by. Each case is set up by
        applying the entry backwards to a solved cube, so the corner is read back off the cube first
        to assert it really sits at UFR in the entry's orientation - it is the key, not the
        algorithm, that recognition has to agree with.

        :param generate_first_layer_case: Fixture generating the case a given insertion algorithm solves
        :param generate_cube: Fixture generating a cube with an algorithm applied
        :param orientation: The orientation at UFR the entry is keyed by
        :param algorithm: The insertion algorithm of that entry
        :return: None
        """

        # Generate the case
        cube = generate_first_layer_case(algorithm)

        # Assert the case is the one the entry is keyed by
        assert search_corner(cube, *FRONT_RIGHT_CORNER) == (CornerSlot.UFR, orientation)

        # Insert the corner
        Rotator(cube).apply(Algorithm.from_str(algorithm))

        # Assert the whole DOWN layer is solved
        solved = generate_cube(2, "")
        assert all(_corner_at(cube, slot) == _corner_at(solved, slot) for slot in DOWN_SLOTS)
