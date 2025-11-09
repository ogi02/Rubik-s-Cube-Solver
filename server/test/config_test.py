# Python imports
import pytest


@pytest.mark.parametrize("constant_name", ["JWT_SECRET", "SOLVER_API_KEY", "VISUALIZER_API_KEY"])
def test_exception_missing_constant(update_env_variable, constant_name):
    """
    Tests that a ValueError is raised when accessing a missing constant.

    :param update_env_variable: Fixture to update environment variables
    :param constant_name: The name of the constant to test
    """

    with pytest.MonkeyPatch.context() as monkeypatch:
        with pytest.raises(ValueError):
            # Update the constant to be missing
            update_env_variable(monkeypatch, constant_name, "")
