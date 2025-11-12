# Python imports
from typing import Callable

import pytest


@pytest.mark.parametrize("constant_name", ["JWT_SECRET", "SOLVER_API_KEY", "VISUALIZER_API_KEY"])
def test_missing_constant_exception(
    update_env_variable: Callable[[pytest.MonkeyPatch, str, str | None], None], constant_name: str
):
    """
    Tests that a ValueError is raised when accessing a missing constant.

    :param update_env_variable: Fixture to update environment variables
    :param constant_name: The name of the constant to test
    """

    with pytest.MonkeyPatch.context() as monkeypatch, pytest.raises(ValueError):
        # Update the constant to be missing
        update_env_variable(monkeypatch, constant_name, "")
