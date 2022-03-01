from .base import APIObject, StrEnum


class PowerStateValue(StrEnum):
    """TV power state values."""

    ON = "On"
    STANDBY = "Standby"


class PowerState(APIObject):
    """Model of a power state request and response."""

    powerstate: PowerStateValue
    """A power state value."""
