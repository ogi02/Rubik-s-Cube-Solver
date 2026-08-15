# Project imports
from rubik_cube_solver.enums.Direction import Direction
from rubik_cube_solver.enums.Layer import Layer
from rubik_cube_solver.enums.Rotation import Rotation

# Maps for cube rotation
CUBE_ROTATION_MAP: dict[tuple[Rotation, Direction], tuple[dict[Layer, Layer], dict[Layer, Direction]]] = {
    (Rotation.X, Direction.CW): (
        {
            Layer.UP: Layer.BACK,
            Layer.BACK: Layer.DOWN,
            Layer.DOWN: Layer.FRONT,
            Layer.FRONT: Layer.UP,
        },
        {
            Layer.DOWN: Direction.DOUBLE,
            Layer.BACK: Direction.DOUBLE,
            Layer.LEFT: Direction.CCW,
            Layer.RIGHT: Direction.CW,
        },
    ),
    (Rotation.X, Direction.CCW): (
        {
            Layer.UP: Layer.FRONT,
            Layer.FRONT: Layer.DOWN,
            Layer.DOWN: Layer.BACK,
            Layer.BACK: Layer.UP,
        },
        {
            Layer.UP: Direction.DOUBLE,
            Layer.BACK: Direction.DOUBLE,
            Layer.LEFT: Direction.CW,
            Layer.RIGHT: Direction.CCW,
        },
    ),
    (Rotation.X, Direction.DOUBLE): (
        {
            Layer.UP: Layer.DOWN,
            Layer.DOWN: Layer.UP,
            Layer.FRONT: Layer.BACK,
            Layer.BACK: Layer.FRONT,
        },
        {
            Layer.FRONT: Direction.DOUBLE,
            Layer.BACK: Direction.DOUBLE,
            Layer.LEFT: Direction.DOUBLE,
            Layer.RIGHT: Direction.DOUBLE,
        },
    ),
    (Rotation.Y, Direction.CW): (
        {
            Layer.FRONT: Layer.LEFT,
            Layer.LEFT: Layer.BACK,
            Layer.BACK: Layer.RIGHT,
            Layer.RIGHT: Layer.FRONT,
        },
        {
            Layer.UP: Direction.CW,
            Layer.DOWN: Direction.CCW,
        },
    ),
    (Rotation.Y, Direction.CCW): (
        {
            Layer.FRONT: Layer.RIGHT,
            Layer.RIGHT: Layer.BACK,
            Layer.BACK: Layer.LEFT,
            Layer.LEFT: Layer.FRONT,
        },
        {
            Layer.UP: Direction.CCW,
            Layer.DOWN: Direction.CW,
        },
    ),
    (Rotation.Y, Direction.DOUBLE): (
        {
            Layer.FRONT: Layer.BACK,
            Layer.BACK: Layer.FRONT,
            Layer.LEFT: Layer.RIGHT,
            Layer.RIGHT: Layer.LEFT,
        },
        {
            Layer.UP: Direction.DOUBLE,
            Layer.DOWN: Direction.DOUBLE,
        },
    ),
    (Rotation.Z, Direction.CW): (
        {
            Layer.UP: Layer.RIGHT,
            Layer.RIGHT: Layer.DOWN,
            Layer.DOWN: Layer.LEFT,
            Layer.LEFT: Layer.UP,
        },
        {
            Layer.UP: Direction.CW,
            Layer.DOWN: Direction.CW,
            Layer.LEFT: Direction.CW,
            Layer.RIGHT: Direction.CW,
            Layer.FRONT: Direction.CW,
            Layer.BACK: Direction.CCW,
        },
    ),
    (Rotation.Z, Direction.CCW): (
        {
            Layer.UP: Layer.LEFT,
            Layer.LEFT: Layer.DOWN,
            Layer.DOWN: Layer.RIGHT,
            Layer.RIGHT: Layer.UP,
        },
        {
            Layer.UP: Direction.CCW,
            Layer.DOWN: Direction.CCW,
            Layer.LEFT: Direction.CCW,
            Layer.RIGHT: Direction.CCW,
            Layer.FRONT: Direction.CCW,
            Layer.BACK: Direction.CW,
        },
    ),
    (Rotation.Z, Direction.DOUBLE): (
        {
            Layer.UP: Layer.DOWN,
            Layer.DOWN: Layer.UP,
            Layer.LEFT: Layer.RIGHT,
            Layer.RIGHT: Layer.LEFT,
        },
        {
            Layer.UP: Direction.DOUBLE,
            Layer.DOWN: Direction.DOUBLE,
            Layer.LEFT: Direction.DOUBLE,
            Layer.RIGHT: Direction.DOUBLE,
            Layer.FRONT: Direction.DOUBLE,
            Layer.BACK: Direction.DOUBLE,
        },
    ),
}

# Maps a layer written after a whole-cube rotation back to the layer it refers to before the rotation.
# `CUBE_ROTATION_MAP` sends the face at position `old` to position `new`, so the face a move names after
# the rotation is the one that used to sit at the inverse position. Layers that the rotation leaves in
# place map to themselves.
MOVE_TRANSLATION_MAP: dict[tuple[Rotation, Direction], dict[Layer, Layer]] = {}
for rotation_key, (rotation_order, _) in CUBE_ROTATION_MAP.items():
    inverted_order: dict[Layer, Layer] = {new: old for old, new in rotation_order.items()}
    MOVE_TRANSLATION_MAP[rotation_key] = {layer: inverted_order.get(layer, layer) for layer in Layer}
