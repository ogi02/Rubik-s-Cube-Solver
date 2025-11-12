# Rubik's Cube Solver

[![TestPyPI version](https://img.shields.io/pypi/v/rubik-cube-solver?label=testpypi&color=blue&logo=pypi)](https://test.pypi.org/project/rubik-cube-solver/)
[![Lint](https://img.shields.io/github/actions/workflow/status/ogi02/Rubik-s-Cube-Solver/solver-lint.yml?branch=main&label=Lint)](https://github.com/ogi02/Rubik-s-Cube-Solver/actions)
[![Pytest](https://img.shields.io/github/actions/workflow/status/ogi02/Rubik-s-Cube-Solver/solver-test.yml?branch=main&label=Pytest)](https://github.com/ogi02/Rubik-s-Cube-Solver/actions)
[![Coverage](https://codecov.io/gh/ogi02/Rubik-s-Cube-Solver/branch/main/graph/badge.svg)](https://codecov.io/gh/ogi02/Rubik-s-Cube-Solver)

A Python library for solving Rubik’s Cubes of various sizes (2×2 → N×N), with support for generating scrambles, performing rotations, and managing cube state.

---

## Installation

The package is located in the [Test PyPI repository](https://test.pypi.org/project/rubiks-cube-solver/). You can install it using pip:

```bash
pip install -i https://test.pypi.org/simple/ rubik-cube-solver
```

## Usage Examples

1. Generating a `Cube` and `Rotator`

```python
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.rotator import Rotator

# Initialize a 3x3 cube
cube = Cube(size=3)

# Initialize the rotator with the cube
rotator = Rotator(cube)
```

2. Turning a `Layer` Using a `Move`

```python
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.move import Move
from rubik_cube_solver.cube_rotation.rotator import Rotator
from rubik_cube_solver.enums.Direction import Direction
from rubik_cube_solver.enums.Layer import Layer

# Initialize cube and rotator
cube = Cube(size=3)
rotator = Rotator(cube)

# Create a move instance
move = Move(layer=Layer.UP, direction=Direction.CW, layer_amount=1)

# Apply the turn
rotator.turn(move)
```

3. Generating a Scramble

```python
from rubik_cube_solver.scramble.scrambler import Scrambler

# Initialize scrambler
scrambler = Scrambler()

# Generate a scramble for a 3x3 cube
scramble_moves = scrambler.generate_scramble(cube_size=3)

for move in scramble_moves:
    print(move)
```

4. Apply a Scramble to a 3×3 Cube

```python
from rubik_cube_solver.cube import Cube
from rubik_cube_solver.cube_rotation.rotator import Rotator
from rubik_cube_solver.scramble.scrambler import Scrambler

# Initialize cube, rotator, and scrambler
cube = Cube(size=3)
rotator = Rotator(cube)
scrambler = Scrambler()

# Print the initial cube state
print(f"\nInitial cube state: \n{cube}")

# Generate a scramble
scramble_moves = scrambler.generate_scramble(cube_size=3)

# Print the scramble
print(f"Scramble: {" ".join(str(move) for move in scramble_moves)}")

# Apply each move to the cube
for move in scramble_moves:
    rotator.turn(move)

# Print the cube state
print(f"\nScrambled cube state: \n{cube}\n")
```

Sample Output:
```text
Initial cube state: 
      W W W
      W W W
      W W W
O O O G G G R R R B B B
O O O G G G R R R B B B
O O O G G G R R R B B B
      Y Y Y
      Y Y Y
      Y Y Y

Scramble: D2 F2 D B' L2 B R F U L2 B2 F' L' D2 L2 F' R2 L' B' R2

Scrambled cube state: 
      B R W
      B W W
      G G R
O Y O Y W Y B B O G B Y
O O G O G G R R Y R B B
R O G R W G W R B W G B
      Y O R
      Y Y W
      W Y O
```

## Contact
Author: [Ognian Baruh](https://github.com/ogi02)  
Email: [ognian@baruh.net](mailto:ognian@baruh.net)