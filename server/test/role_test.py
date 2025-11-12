# Python imports
import pytest

# Project imports
from role import Role


# fmt: off
@pytest.mark.parametrize(
    "role_str, expected_role", [
        ("SOLVER",     Role.SOLVER),
        ("VISUALIZER", Role.VISUALIZER)
    ])
# fmt: on
def test_role_from_str_success(role_str: str, expected_role: Role) -> None:
    """
    Tests that Role.from_str correctly converts strings to Role enums.

    :param role_str: The string representation of the role
    :param expected_role: The expected Role enum member
    """

    assert Role.from_str(role_str) == expected_role


def test_role_from_str_exception() -> None:
    """
    Tests that Role.from_str raises ValueError for invalid role strings.
    """

    with pytest.raises(ValueError) as exc_info:
        Role.from_str("INVALID_ROLE")

    assert str(exc_info.value) == "Unknown role: INVALID_ROLE"
