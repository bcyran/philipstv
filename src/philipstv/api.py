from typing import Any, Optional, Type, TypeVar

from ._interfaces import PhilipsTVInterface
from .model import (
    AllChannels,
    AmbilightColors,
    AmbilightColorSettings,
    AmbilightMode,
    AmbilightPower,
    AmbilightTopology,
    APIModel,
    Applications,
    ApplicationShort,
    CurrentChannel,
    CurrentVolume,
    InputKey,
    PairingGrantPayload,
    PairingRequestPayload,
    PairingRequestResponse,
    PairingResponse,
    PowerState,
    SetChannel,
    Volume,
)
from .types import Credentials

_T = TypeVar("_T", bound=APIModel)


class PhilipsTVAPI:
    def __init__(self, tv: PhilipsTVInterface) -> None:
        self._tv = tv
        self.api_version = 6

    def set_auth(self, auth: Optional[Credentials]) -> None:
        self._tv.set_auth(auth)

    def pair_request(self, payload: PairingRequestPayload) -> PairingRequestResponse:
        return self._api_post_model("pair/request", PairingRequestResponse, payload)

    def pair_grant(self, payload: PairingGrantPayload) -> PairingResponse:
        return self._api_post_model("pair/grant", PairingResponse, payload)

    def get_powerstate(self) -> PowerState:
        return self._api_get_model("powerstate", PowerState)

    def set_powerstate(self, powerstate: PowerState) -> None:
        self._api_post("powerstate", powerstate)

    def get_volume(self) -> CurrentVolume:
        return self._api_get_model("audio/volume", CurrentVolume)

    def set_volume(self, volume: Volume) -> None:
        self._api_post("audio/volume", volume)

    def get_current_channel(self) -> CurrentChannel:
        return self._api_get_model("activities/tv", CurrentChannel)

    def get_all_channels(self) -> AllChannels:
        return self._api_get_model("channeldb/tv/channelLists/all", AllChannels)

    def set_channel(self, channel: SetChannel) -> None:
        self._api_post("activities/tv", channel)

    def input_key(self, key: InputKey) -> None:
        self._api_post("input/key", key)

    def get_ambilight_power(self) -> AmbilightPower:
        return self._api_get_model("ambilight/power", AmbilightPower)

    def set_ambilight_power(self, power: AmbilightPower) -> None:
        self._api_post("ambilight/power", power)

    def get_ambilight_topology(self) -> AmbilightTopology:
        return self._api_get_model("ambilight/topology", AmbilightTopology)

    def get_ambilight_mode(self) -> AmbilightMode:
        return self._api_get_model("ambilight/mode", AmbilightMode)

    def set_ambilight_mode(self, mode: AmbilightMode) -> None:
        self._api_post("ambilight/mode", mode)

    def get_ambilight_measured(self) -> AmbilightColors:
        return self._api_get_model("ambilight/measured", AmbilightColors)

    def get_ambilight_processed(self) -> AmbilightColors:
        return self._api_get_model("ambilight/processed", AmbilightColors)

    def get_ambilight_cached(self) -> AmbilightColors:
        return self._api_get_model("ambilight/cached", AmbilightColors)

    def set_ambilight_cached(self, colors: AmbilightColorSettings) -> None:
        self._api_post("ambilight/cached", colors)

    def get_applications(self) -> Applications:
        return self._api_get_model("applications", Applications)

    def launch_application(self, application: ApplicationShort) -> None:
        self._api_post("activities/launch", application)

    def _api_post_model(
        self, path: str, resp_model: Type[_T], payload: Optional[APIModel] = None
    ) -> _T:
        return resp_model.parse(self._api_post(path, payload))

    def _api_get_model(self, path: str, response_model: Type[_T]) -> _T:
        return response_model.parse(self._api_get(path))

    def _api_post(self, path: str, payload: Optional[APIModel] = None) -> Any:
        return self._tv.post(self._api_path(path), payload.dump() if payload else None)

    def _api_get(self, path: str) -> Any:
        return self._tv.get(self._api_path(path))

    def _api_path(self, path: str) -> str:
        return f"{self.api_version}/{path}"
