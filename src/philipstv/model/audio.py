from .base import APIObject


class Volume(APIObject):
    """Model of a volume set request."""

    current: int
    """Volume value."""
    muted: bool = False
    """Whether the TV is muted."""


class CurrentVolume(Volume):
    """Model of a volume response."""

    min: int
    """Minimum allowed volume value."""
    max: int
    """Maximum allowed volume value."""
