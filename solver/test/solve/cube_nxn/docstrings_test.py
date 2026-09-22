# Python imports
import doctest
from types import ModuleType

import pytest

# Project imports
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.algorithm import Algorithm
from rubik_cube_solver.cube_rotation.rotator import Rotator
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.Direction import Direction
from rubik_cube_solver.enums.EdgeSlot import EdgeSlot
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.solve.center_search import CenterSearchResult
from rubik_cube_solver.solve.cube_nxn import centers, edges, last_centers, pieces, routes

# The names the examples use without importing them: the types every example builds its cube from,
# and the functions and constants of all five modules, since an example in one module may use a
# constant from another.
EXAMPLE_GLOBALS: dict = {
    **vars(pieces),
    **vars(routes),
    **vars(centers),
    **vars(last_centers),
    **vars(edges),
    "Algorithm": Algorithm,
    "CenterSearchResult": CenterSearchResult,
    "Color": Color,
    "Cube": Cube,
    "Direction": Direction,
    "EdgeSlot": EdgeSlot,
    "Layer": Layer,
    "Rotator": Rotator,
}


class TestDocstringExamples:
    # fmt: off
    @pytest.mark.parametrize("module", [pieces, routes, centers, last_centers, edges])
    # fmt: on
    def test_success(self, module: ModuleType) -> None:
        """
        Tests that every example in a module's docstrings produces the output it shows, so an example
        cannot drift out of step with the code it describes.

        :param module: The module whose docstring examples are run
        :return: None
        """

        # Run the examples
        result = doctest.testmod(module, globs=dict(EXAMPLE_GLOBALS), optionflags=doctest.NORMALIZE_WHITESPACE)

        # Assert
        assert result.attempted > 0
        assert result.failed == 0
