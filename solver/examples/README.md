# Examples

Runnable scripts showing how to use the `rubik_cube_solver` library. Each script stands on its own,
prints what it is doing, and can be read top to bottom.

## Running them

Install the library, then run any script from the `solver/` directory:

```bash
pip install -e .
python examples/01_create_cube.py
```

Every script apart from `04_scrambling.py` uses a fixed scramble, so its output is the same on every
run. Each script is split into numbered sections, listed in its `SECTIONS` table and printed above
the output they produce, so every block of output can be traced back to the function behind it.

## The scripts

| Script | What it shows |
| --- | --- |
| [`01_create_cube.py`](01_create_cube.py) | Creating cubes of any size, printing the net, reading single stickers, and building a cube from an explicit sticker layout. |
| [`02_rotator_and_moves.py`](02_rotator_and_moves.py) | Turning layers with `Rotator` and `Move`, parsing and printing standard notation, wide turns, and whole-cube rotations. |
| [`03_algorithms.py`](03_algorithms.py) | Parsing an `Algorithm` from notation, applying it with `Rotator.apply`, the notation round trip, and building an algorithm from `Move` objects. |
| [`04_scrambling.py`](04_scrambling.py) | Generating random scrambles with `Scrambler` for cubes of different sizes and applying one to a cube. |
| [`05_validating.py`](05_validating.py) | Validating reachable states with `Validator`, and the errors raised by a miscounted color, a twisted corner, and a swapped pair of edges. |
| [`06_solve_2x2.py`](06_solve_2x2.py) | Solving a 2x2 with `Solve2x2`, replaying the returned solution on a second cube, and the size check. |
| [`07_solve_3x3.py`](07_solve_3x3.py) | Solving a 3x3 with `Solve3x3`, reading the solution back, and the size check. |
