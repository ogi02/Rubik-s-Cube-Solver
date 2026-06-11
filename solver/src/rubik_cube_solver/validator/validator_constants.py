# Project imports
from rubik_cube_solver.enums.Color import Color
from rubik_cube_solver.enums.Layer import Layer

VALID_CORNER_COLOR_SETS: frozenset[frozenset[Color]] = frozenset(
    {
        frozenset({Color.WHITE, Color.GREEN, Color.ORANGE}),
        frozenset({Color.WHITE, Color.GREEN, Color.RED}),
        frozenset({Color.WHITE, Color.BLUE, Color.ORANGE}),
        frozenset({Color.WHITE, Color.BLUE, Color.RED}),
        frozenset({Color.YELLOW, Color.GREEN, Color.ORANGE}),
        frozenset({Color.YELLOW, Color.GREEN, Color.RED}),
        frozenset({Color.YELLOW, Color.BLUE, Color.ORANGE}),
        frozenset({Color.YELLOW, Color.BLUE, Color.RED}),
    }
)

# Canonical CW sequence for each valid corner color set
CORNER_CANONICAL_CW: dict[frozenset[Color], tuple[Color, Color, Color]] = {
    frozenset({Color.WHITE, Color.GREEN, Color.ORANGE}): (Color.WHITE, Color.GREEN, Color.ORANGE),
    frozenset({Color.WHITE, Color.GREEN, Color.RED}): (Color.WHITE, Color.RED, Color.GREEN),
    frozenset({Color.WHITE, Color.BLUE, Color.ORANGE}): (Color.WHITE, Color.ORANGE, Color.BLUE),
    frozenset({Color.WHITE, Color.BLUE, Color.RED}): (Color.WHITE, Color.BLUE, Color.RED),
    frozenset({Color.YELLOW, Color.GREEN, Color.ORANGE}): (Color.YELLOW, Color.ORANGE, Color.GREEN),
    frozenset({Color.YELLOW, Color.GREEN, Color.RED}): (Color.YELLOW, Color.GREEN, Color.RED),
    frozenset({Color.YELLOW, Color.BLUE, Color.ORANGE}): (Color.YELLOW, Color.BLUE, Color.ORANGE),
    frozenset({Color.YELLOW, Color.BLUE, Color.RED}): (Color.YELLOW, Color.RED, Color.BLUE),
}

VALID_EDGE_COLOR_SETS: frozenset[frozenset[Color]] = frozenset(
    {
        frozenset({Color.WHITE, Color.GREEN}),
        frozenset({Color.WHITE, Color.BLUE}),
        frozenset({Color.WHITE, Color.ORANGE}),
        frozenset({Color.WHITE, Color.RED}),
        frozenset({Color.YELLOW, Color.GREEN}),
        frozenset({Color.YELLOW, Color.BLUE}),
        frozenset({Color.YELLOW, Color.ORANGE}),
        frozenset({Color.YELLOW, Color.RED}),
        frozenset({Color.GREEN, Color.ORANGE}),
        frozenset({Color.GREEN, Color.RED}),
        frozenset({Color.BLUE, Color.ORANGE}),
        frozenset({Color.BLUE, Color.RED}),
    }
)

# For each edge color set, the primary color is the one that should face UP/DOWN (for U/D edges)
# or FRONT/BACK (for equatorial edges) to be considered "oriented" (orientation = 0)
EDGE_CANONICAL_ORIENTATION: dict[frozenset[Color], Color] = {
    frozenset({Color.WHITE, Color.GREEN}): Color.WHITE,
    frozenset({Color.WHITE, Color.BLUE}): Color.WHITE,
    frozenset({Color.WHITE, Color.ORANGE}): Color.WHITE,
    frozenset({Color.WHITE, Color.RED}): Color.WHITE,
    frozenset({Color.YELLOW, Color.GREEN}): Color.YELLOW,
    frozenset({Color.YELLOW, Color.BLUE}): Color.YELLOW,
    frozenset({Color.YELLOW, Color.ORANGE}): Color.YELLOW,
    frozenset({Color.YELLOW, Color.RED}): Color.YELLOW,
    frozenset({Color.GREEN, Color.ORANGE}): Color.GREEN,
    frozenset({Color.GREEN, Color.RED}): Color.GREEN,
    frozenset({Color.BLUE, Color.ORANGE}): Color.BLUE,
    frozenset({Color.BLUE, Color.RED}): Color.BLUE,
}

CENTER_COLORS_OPPOSITES: dict[Color, Color] = {
    Color.WHITE: Color.YELLOW,
    Color.YELLOW: Color.WHITE,
    Color.GREEN: Color.BLUE,
    Color.BLUE: Color.GREEN,
    Color.ORANGE: Color.RED,
    Color.RED: Color.ORANGE,
}

CENTER_LAYER_OPPOSITES: dict[Layer, Layer] = {
    Layer.UP: Layer.DOWN,
    Layer.DOWN: Layer.UP,
    Layer.FRONT: Layer.BACK,
    Layer.BACK: Layer.FRONT,
    Layer.LEFT: Layer.RIGHT,
    Layer.RIGHT: Layer.LEFT,
}
