from ._base import APIObject, StrEnum


class PowerStateValue(StrEnum):
    ON = "On"
    STANDBY = "Standby"


class PowerState(APIObject):
    powerstate: PowerStateValue
