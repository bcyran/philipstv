from typing import Dict, Union

from pydantic.fields import Field

from ._base import APIObject, StrEnum


class AmbilightPowerValue(StrEnum):
    ON = "On"
    OFF = "Off"


class AmbilightPower(APIObject):
    power: AmbilightPowerValue


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


class AmbilightLayer(APIObject):
    left: Dict[str, AmbilightColor] = Field(default_factory=dict)
    top: Dict[str, AmbilightColor] = Field(default_factory=dict)
    right: Dict[str, AmbilightColor] = Field(default_factory=dict)
    bottom: Dict[str, AmbilightColor] = Field(default_factory=dict)


class AmbilightColors(APIObject):
    __root__: Dict[str, AmbilightLayer]

    def __getitem__(self, item: str) -> AmbilightLayer:
        return self.__root__[item]


AmbilightColorSettings = Union[
    AmbilightColor,  # single color for all pixels
    AmbilightColors,  # individual pixels
]
