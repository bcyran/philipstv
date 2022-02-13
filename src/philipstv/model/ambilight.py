from typing import Dict, Union

from pydantic.fields import Field

from .base import APIObject, StrEnum


class AmbilightTopology(APIObject):
    layers: int
    left: int
    top: int
    right: int
    bottom: int


class AmbilightModeValue(StrEnum):
    INTERNAL = "internal"
    MANUAL = "manual"
    EXPERT = "expert"


class AmbilightMode(APIObject):
    current: AmbilightModeValue


class AmbilightColor(APIObject):
    r: int = Field(ge=0, le=255)
    g: int = Field(ge=0, le=255)
    b: int = Field(ge=0, le=255)


class AmbilightPixels(APIObject):
    __root__: Dict[str, AmbilightColor] = Field(default_factory=dict)

    def __getitem__(self, item: str) -> AmbilightColor:
        return self.__root__[item]


class AmbilightLayer(APIObject):
    left: AmbilightPixels = Field(default_factory=AmbilightPixels)
    top: AmbilightPixels = Field(default_factory=AmbilightPixels)
    right: AmbilightPixels = Field(default_factory=AmbilightPixels)
    bottom: AmbilightPixels = Field(default_factory=AmbilightPixels)


class AmbilightColors(APIObject):
    __root__: Dict[str, AmbilightLayer]

    def __getitem__(self, item: str) -> AmbilightLayer:
        return self.__root__[item]


AmbilightColorSettings = Union[
    AmbilightColor,  # single color for all pixels
    AmbilightColors,  # individual pixels
]
