from dataclasses import dataclass

from .base import APIDataClass


@dataclass(frozen=True)
class Volume(APIDataClass):
    muted: bool
    current: int
    min: int
    max: int


@dataclass(frozen=True)
class NewVolume(APIDataClass):
    current: int
    muted: bool = False
