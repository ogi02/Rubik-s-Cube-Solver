# Rubik's Cube Solver

[![Lint](https://img.shields.io/github/actions/workflow/status/ogi02/Rubik-s-Cube-Solver/solver-lint.yml?branch=main&label=Lint)](https://github.com/ogi02/Rubik-s-Cube-Solver/actions)
[![Pytest](https://img.shields.io/github/actions/workflow/status/ogi02/Rubik-s-Cube-Solver/solver-test.yml?branch=main&label=Pytest)](https://github.com/ogi02/Rubik-s-Cube-Solver/actions)
[![Coverage](https://codecov.io/gh/ogi02/Rubik-s-Cube-Solver/branch/main/graph/badge.svg)](https://codecov.io/gh/ogi02/Rubik-s-Cube-Solver)

A Python library for Rubik's Cubes of any size. It represents the cube state, turns and rotates it
in standard notation, generates scrambles, checks whether a state is reachable, and solves the 2x2
and the 3x3 the way a human does.

---

## Installation

The package is published to the [Test PyPI repository](https://test.pypi.org/project/rubik-cube-solver/)
and requires Python 3.13 or newer:

```bash
pip install -i https://test.pypi.org/simple/ rubik-cube-solver
```

## Functionality

### Cube Representation

`Cube` is the state of a single puzzle. It is created from its size — `Cube(size=3)` — and any size
from 2x2 upwards is supported. The six faces are held in a dictionary keyed by `Layer`, each face a
flat, row-major list of `Color` values, so a face of an N x N cube is a list of N x N stickers. A new
cube starts solved in the standard color scheme: white on UP, yellow on DOWN, orange on LEFT, red on
RIGHT, green on FRONT and blue on BACK. A cube can also be built from an explicit sticker layout by
passing the `layers` dictionary, which is how a scanned or received state is loaded.

Two readers are provided on top of the raw stickers. `str(cube)` renders the classic unfolded net,
which is what the examples print. `state()` returns a plain dictionary of the cube's dimensions and
its faces keyed by name, ready to be serialized and sent to the visualizer over the WebSocket
connection.

### Moves, Rotations and Algorithms

A `Move` is one turn: a `Layer` (UP, DOWN, LEFT, RIGHT, FRONT, BACK) or a `Rotation` axis (x, y, z),
a `Direction` (clockwise, counter-clockwise or double), and the number of layers the turn takes with
it. That covers outer turns, wide turns on big cubes and whole-cube rotations in one type. Moves read
and write standard notation — `Move.from_str` parses `R`, `U'`, `F2`, `Rw`, `3Lw'`, `x` and `y2`, and
`str(move)` gives the same string back, so notation can be round-tripped through the library.

`Rotator` is bound to a cube and applies moves to it. `turn` performs a single move, moving both the
stickers on the turned face and the bands of stickers on the four adjacent faces; `rotate` reorients
the whole cube around an axis; and `apply` runs a whole algorithm in order.

An `Algorithm` is a sequence of moves with the operations that sequences need. `Algorithm.from_str`
parses a whole line of notation and `str()` prints it back. `merge` appends another algorithm, which
is how a solution is accumulated step by step. `cancel_moves` reduces adjacent moves on the same
layer, so `R U U' R2` becomes `R'`. `remove_rotations` rewrites an algorithm containing whole-cube
rotations into an equivalent one made only of layer turns, so `x R U R' U'` becomes `R F R' F'` —
necessary when the moves are handed to a machine that cannot pick the cube up and turn it around.

### Scrambling

`Scrambler` generates random scrambles for a cube of a given size, returning them as a list of
`Move` objects that can be applied with `Rotator`. The length follows the size: 8 moves for a 2x2,
20 for a 3x3, and 20 moves for every layer past the first two on bigger cubes — 40 for a 4x4, 60 for
a 5x5, and so on. The generator never produces a redundant
sequence — it does not repeat a face, and it does not return to a face until the axis has changed.
A 2x2 is scrambled with UP, FRONT and RIGHT turns only, since turning an opposite face of a 2x2 just
reorients the puzzle, and cubes of 4x4 and larger also receive wide turns.

### Validation

`Validator.validate` decides whether a cube state can actually occur, raising a `ValueError` naming
the first problem it finds. This matters most for states that come from outside the library, such as
a cube scanned by a camera, where a misread sticker would otherwise send the solver into an infinite
loop.

The checks scale with the cube. Every cube is checked for a valid size, for the right number of
stickers of each color, and for corner pieces that exist, are oriented consistently and are not
mirrored. Odd cubes additionally have their fixed centers checked for uniqueness and for correct
opposite pairs, and their edges checked for existence, flip parity and permutation parity. Cubes of
4x4 and larger have their center pieces counted and their wing edges checked for valid color pairs.

### Solving

Solvers share the `Solve` base class, which holds the cube, the rotator and the algorithm collected
so far. Calling `solve()` runs the ordered steps of the method, applies every move to the cube, and
returns the complete solution as an `Algorithm` — the cube is left solved and the solution can be
replayed on a second cube, printed as notation, or sent on to the visualizer or the machine.

`create_solver` is the entry point: it takes any cube, reads its size and returns the solver for
it, so callers never pick a class themselves. A size no solver handles is rejected there and then,
before any solving starts.

`Solve2x2` solves the 2x2 layer by layer: the first layer, then the orientation of the last layer,
then its permutation. `Solve3x3` follows CFOP: the cross, the first two layers, the orientation of
the last layer and its permutation. Both are human methods rather than searches, so the solutions
are the ones a person would recognize rather than the shortest ones. Either can still be
constructed directly, and each accepts only its own cube size.

Cubes of 4x4 and larger are fully supported by every other part of the library — representation,
turning, scrambling and validation — but no solver exists for them yet.

## Examples

Runnable scripts covering all of the above live in [`examples/`](examples/README.md). Install the
library and run any of them from the `solver/` directory:

```bash
python examples/01_create_cube.py
```

| Script | What it shows |
| --- | --- |
| [`01_create_cube.py`](examples/01_create_cube.py) | Creating cubes of any size, printing the net, reading single stickers, and building a cube from an explicit sticker layout. |
| [`02_rotator_and_moves.py`](examples/02_rotator_and_moves.py) | Turning layers with `Rotator` and `Move`, parsing and printing standard notation, wide turns, and whole-cube rotations. |
| [`03_algorithms.py`](examples/03_algorithms.py) | Parsing an `Algorithm` from notation, applying it, the notation round trip, and building an algorithm from `Move` objects. |
| [`04_scrambling.py`](examples/04_scrambling.py) | Generating random scrambles with `Scrambler` for cubes of different sizes and applying one to a cube. |
| [`05_validating.py`](examples/05_validating.py) | Validating reachable states with `Validator`, and the errors raised by a miscounted color, a twisted corner, and a swapped pair of edges. |
| [`06_solve_2x2.py`](examples/06_solve_2x2.py) | Solving a 2x2 through `create_solver`, replaying the returned solution on a second cube, and a size no solver handles. |
| [`07_solve_3x3.py`](examples/07_solve_3x3.py) | Solving a 3x3 through `create_solver`, reading the solution back, and a size no solver handles. |
| [`08_solve_big_cube.py`](examples/08_solve_big_cube.py) | Building the first four centers of a 4x4 and a 5x5 through `create_solver`, and reading the faces they end up on. |

## Development Setup

Clone the repository and move into this sub-project — the repository has no root-level build, so
every command below is run from `solver/`:

```bash
git clone https://github.com/ogi02/Rubik-s-Cube-Solver.git
cd Rubik-s-Cube-Solver/solver
```

Install the development dependencies, which cover testing, linting, formatting and building:

```bash
pip install -r dev-requirements.txt
```

Install the library itself in editable mode so the examples and the tests import the working copy:

```bash
pip install -e .
```

## Testing

The test suite mirrors the source packages and is run with coverage:

```bash
pytest test --cov=src --cov-branch --cov-report=term
```

The suite also executes every script in `examples/` and asserts that it exits cleanly, so an API
change that breaks a documented entry point fails the build. The same command runs in the
`Solver Test` workflow on every push and pull request, and uploads the coverage report to Codecov.

## Code Quality

Formatting, import sorting and linting are handled by `black`, `isort` and `flake8`, configured for
a line length of 120 in `pyproject.toml` and `.flake8`. They run over `src`, `test` and `examples`
alike.

The easiest way to run them is through the pre-commit hooks:

```bash
pre-commit install
pre-commit run --all-files
```

The `Solver Lint` workflow runs the same three tools directly on every push and pull request:

```bash
black --check src test examples --config pyproject.toml
isort --check-only src test examples --settings-path pyproject.toml
flake8 src test examples --config .flake8
```

## Building and Publishing

The package is built with `setuptools` from the metadata in `pyproject.toml`. Raise the `version`
field there before publishing, since Test PyPI rejects a version that already exists.

Build the distribution:

```bash
pip install --upgrade build
python -m build
```

Upload it to Test PyPI:

```bash
pip install --upgrade twine
python -m twine upload --repository testpypi dist/*
```

Publishing is a manual step — no workflow releases the package.

## Contact
Author: [Ognian Baruh](https://github.com/ogi02)  
Email: [ognian@baruh.net](mailto:ognian@baruh.net)
