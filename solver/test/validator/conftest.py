# Python imports
import pytest

# Project imports
from rubik_cube_solver.validator.validator import Validator


@pytest.fixture
def validator() -> Validator:
    """
    Returns a Validator instance.

    :return: The Validator instance
    """

    return Validator()
