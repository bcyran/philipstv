from typing import Any

from .base import APIEnum


class PowerState(APIEnum):
    ON = "On"
    STANDBY = "Standby"

    @classmethod
    def parse(cls, raw: Any) -> "PowerState":
        return PowerState(raw["powerstate"])
