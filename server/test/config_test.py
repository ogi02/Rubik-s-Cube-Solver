# Python imports
from typing import Callable

import pytest


class TestConfigConstants:
    """
    Tests for the required config constants.
    """

    @pytest.mark.parametrize("constant_name", ["JWT_SECRET", "SOLVER_API_KEY", "VISUALIZER_API_KEY"])
    def test_invalid_missing_constant(
        self, update_env_variable: Callable[[pytest.MonkeyPatch, str, str | None], None], constant_name: str
    ) -> None:
        """
        Tests that a ValueError is raised when accessing a missing constant.

        :param update_env_variable: Fixture to update environment variables
        :param constant_name: The name of the constant to test
        """

        with pytest.MonkeyPatch.context() as monkeypatch, pytest.raises(ValueError):
            # Update the constant to be missing
            update_env_variable(monkeypatch, constant_name, "")
