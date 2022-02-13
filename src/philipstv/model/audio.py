from .base import APIObject


class CurrentVolume(APIObject):
    muted: bool
    current: int
    min: int
    max: int


class SetVolume(APIObject):
    current: int
    muted: bool = False
