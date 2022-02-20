from ._base import APIObject


class Volume(APIObject):
    current: int
    muted: bool = False


class CurrentVolume(Volume):
    muted: bool
    current: int
    min: int
    max: int
