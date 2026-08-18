# Python imports
import subprocess
import sys
from pathlib import Path

import pytest

SOLVER_DIRECTORY = Path(__file__).resolve().parent.parent
EXAMPLES_DIRECTORY = SOLVER_DIRECTORY / "examples"
EXAMPLE_SCRIPTS = sorted(EXAMPLES_DIRECTORY.glob("*.py"))


class TestExampleScripts:
    def test_scripts_are_collected(self) -> None:
        """
        Tests that the examples directory holds scripts to run.

        Without this, a glob that stopped matching would leave the parametrized test below with no
        cases and the suite would still pass.

        :return: None
        """

        # Assert
        assert EXAMPLE_SCRIPTS

    @pytest.mark.parametrize("script", EXAMPLE_SCRIPTS, ids=lambda script: script.name)
    def test_success(self, script: Path) -> None:
        """
        Tests that an example script runs to completion and prints something.

        The scripts are the documented entry points of the library, so an API change that breaks one
        of them has to fail here.

        :param script: The example script to run
        :return: None
        """

        # Run the script in its own interpreter
        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=SOLVER_DIRECTORY,
            capture_output=True,
            text=True,
        )

        # Assert
        assert result.returncode == 0, f"{script.name} exited with {result.returncode}:\n{result.stderr}"
        assert result.stdout
