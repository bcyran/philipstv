from typing import Dict, Tuple, Union

from pydantic.fields import Field

from .base import APIObject, StrEnum


class AmbilightPowerValue(StrEnum):
    """Ambilight power state values."""

    ON = "On"
    OFF = "Off"


class AmbilightPower(APIObject):
    """Ambilight power state request and response model."""

    power: AmbilightPowerValue
    """Ambilight power state value."""


class AmbilightTopology(APIObject):
    """Ambilight topology response model."""

    layers: int
    """Number of layers."""
    left: int
    """Number of pixels on the left edge."""
    top: int
    """Number of pixels on the top edge."""
    right: int
    """Number of pixels on the right edge."""
    bottom: int
    """Number of pixels on the bottom edge."""


class AmbilightModeValue(StrEnum):
    """Ambilight mode values."""

    INTERNAL = "internal"
    MANUAL = "manual"
    EXPERT = "expert"


class AmbilightMode(APIObject):
    """Ambilight mode request and response model."""

    current: AmbilightModeValue
    """Ambiglight mode value."""


class AmbilightColor(APIObject):
    """Ambilight color model."""

    r: int = Field(ge=0, le=255)
    """Red color component."""
    g: int = Field(ge=0, le=255)
    """Green color component."""
    b: int = Field(ge=0, le=255)
    """Blue color component."""

    @classmethod
    def from_tuple(cls, color_tuple: Tuple[int, int, int]) -> "AmbilightColor":
        """Create :class:`AmbilightColor` instance from a tuple.

        Args:
            color_tuple: Tuple of three integers representing RGB color.

        Returns:
            Model instance.

        """
        return cls(r=color_tuple[0], g=color_tuple[1], b=color_tuple[2])


class AmbilightLayer(APIObject):
    """Model of a single Ambilight layer per-pixel colors definition.

    Each edge is a mappping of a pixel name to it's color::

        layer = AmbilightLayer(top={"0": AmbilightColor(...), "1": AmbilightColor(...)})

    """

    left: Dict[str, AmbilightColor] = Field(default_factory=dict)
    """Colors of pixels on the left edge."""
    top: Dict[str, AmbilightColor] = Field(default_factory=dict)
    """Colors of pixels on the top edge."""
    right: Dict[str, AmbilightColor] = Field(default_factory=dict)
    """Colors of pixels on the right edge."""
    bottom: Dict[str, AmbilightColor] = Field(default_factory=dict)
    """Colors of pixels on the bottom edge."""


class AmbilightColors(APIObject):
    """Model of full Amblight per-pixel color definition.

    This model is actually a wrapper around a dict since layer names are not predefined.
    Values should be set as dict using ``__root__`` kwarg in constructor and accessed as in normal
    dict using indexing::

        colors = AmbilightColors(__root__={"layer1": AmbilightLayer()})
        layer1 = colors["layer1"]

    """

    __root__: Dict[str, AmbilightLayer] = {}
    """Mapping of layer name to :class:`AmbilightLayer`."""

    def __getitem__(self, item: str) -> AmbilightLayer:
        return self.__root__[item]


AmbilightColorSettings = Union[
    AmbilightColor,  # single color for all pixels
    AmbilightColors,  # individual pixels
]
