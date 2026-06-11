# Python imports
import pytest

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.validator.validator import Validator
from rubik_cube_solver.validator.validator_constants import VALID_CORNER_COLOR_SETS, VALID_EDGE_COLOR_SETS
from rubik_cube_solver.validator.validator_utils import get_corners, get_edges


class TestValidatorGetCorners:
    def test_success(self, validator: Validator) -> None:
        """
        Test that _get_corners returns the expected corners.

        :param validator: Fixture of a Validator instance
        :return: None
        """

        cube = Cube(3)
        corners = get_corners(cube)
        expected_corners = VALID_CORNER_COLOR_SETS

        assert len(corners) == len(expected_corners)
        for corner in corners:
            assert isinstance(corner, tuple)
            assert frozenset(corner) in expected_corners


class TestValidatorGetEdges:
    # fmt: off
    @pytest.mark.parametrize(
        "cube_size", [3, 5, 7]
    )
    # fmt: on
    def test_success(self, validator: Validator, cube_size: int) -> None:
        """
        Test that _get_edges returns 12 edge tuples with correct sticker colors for a solved odd sized cube.

        :param validator: Fixture of a Validator instance
        :param cube_size: Fixture of size of the cube
        :return: None
        """

        cube = Cube(cube_size)
        edges = get_edges(cube)
        expected_edges = VALID_EDGE_COLOR_SETS

        assert len(edges) == len(expected_edges)
        for edge in edges:
            assert isinstance(edge, tuple)
            assert frozenset(edge) in expected_edges
