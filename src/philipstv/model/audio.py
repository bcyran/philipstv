from .base import APIObject


class Volume(APIObject):
    muted: bool
    current: int
    min: int
    max: int


class NewVolume(APIObject):
    current: int
    muted: bool = False
