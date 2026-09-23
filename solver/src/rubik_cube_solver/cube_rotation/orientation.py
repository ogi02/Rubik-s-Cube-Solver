# Project imports
from rubik_cube_solver.cube_rotation.cube_rotation import MOVE_TRANSLATION_MAP
from rubik_cube_solver.cube_rotation.move import Move
from rubik_cube_solver.enums.Layer import Layer


class Orientation:
    """
    Represents the way a cube is held, as the layer that every face name refers to.

    A cube held as it was built is the identity orientation, where every name refers to its own
    layer. Each whole-cube rotation moves the faces around, so the same name then refers to a
    different layer.
    """

    def __init__(self, layers: dict[Layer, Layer] | None = None) -> None:
        """
        Constructor for the `Orientation` class.

        :param layers: The layer every face name refers to, or None for a cube held as it was built
        :return: None
        """

        self.__layers = layers if layers is not None else {layer: layer for layer in Layer}

    @property
    def layers(self) -> dict[Layer, Layer]:
        """
        Layers getter.

        :return: The layer every face name refers to
        """

        return self.__layers

    def __eq__(self, other) -> bool:
        """
        Equality comparison for Orientation objects.

        :param other: The other Orientation object to compare with
        :return: True if equal, False otherwise
        """

        if not isinstance(other, Orientation):
            return False

        return self.__layers == other.layers

    def rotate(self, rotation: Move) -> "Orientation":
        """
        Return the orientation the cube is held in after a whole-cube rotation.

        The rotation sends the face at every position to a new one, so a name written after it
        refers to the layer that used to sit at the position the name now points at. This
        orientation is left untouched.

        Example: rotating the identity orientation by `x` makes `UP` refer to `FRONT`.

        :param rotation: The whole-cube rotation to perform
        :return: The orientation after the rotation
        """

        translation = MOVE_TRANSLATION_MAP[(rotation.layer, rotation.direction)]

        return Orientation({layer: self.__layers[translation[layer]] for layer in Layer})
