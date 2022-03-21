from contextlib import contextmanager
from typing import Any, Iterator, Optional, Type, TypeVar

from philipstv.exceptions import (
    PhilipsTVAPIMalformedResponseError,
    PhilipsTVAPIUnauthorizedError,
    PhilipsTVError,
)

from .model import (
    AllChannels,
    AmbilightColors,
    AmbilightColorSettings,
    AmbilightMode,
    AmbilightPower,
    AmbilightTopology,
    APIObject,
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
    ValidationError,
    Volume,
)
from .tv import PhilipsTV
from .types import Credentials

_T = TypeVar("_T", bound=APIObject)


@contextmanager
def _wrap_unauthorized_exceptions(path: str) -> Iterator[None]:
    try:
        yield
    except PhilipsTVError as exc:
        if exc.status_code == 401:
            raise PhilipsTVAPIUnauthorizedError(exc.method, path) from exc
        raise


@contextmanager
def _wrap_validation_exceptions(method: str, path: str, response: Any) -> Iterator[None]:
    try:
        yield
    except ValidationError as exc:
        raise PhilipsTVAPIMalformedResponseError(method, path, response) from exc


class PhilipsTVAPI:
    """Wrapper around Philips TV API.

    Each method mirrors a single `GET` or `POST` request to one of the available API endpoints.
    The original shape of request payloads and responses in preserved, but they're wrapped
    in `pydantic` models.

    """

    def __init__(self, tv: PhilipsTV) -> None:
        """
        Args:
            tv: Instance of the :class:`PhilipsTV` to which the API requestes will be sent.

        """
        self._tv = tv
        self.api_version = 6

    @property
    def host(self) -> str:
        """IP address of the underlying :class:`PhilipsTV` instance.

        Warning:
            This value is read-only.

        """
        return self._tv.host

    @property
    def auth(self) -> Optional[Credentials]:
        """Credentials used for authentication in the underlying :class:`PhilipsTV` instance.

        Hint:
            This value can be set and changed at any moment during :class:`PhilipsTVAPI` usage.

        """
        return self._tv.auth

    @auth.setter
    def auth(self, auth: Optional[Credentials]) -> None:
        self._tv.auth = auth

    def pair_request(self, payload: PairingRequestPayload) -> PairingRequestResponse:
        """Send request initiating the pairing process.

        Use :func:`pair_grant` to finalize the pairing using data from response to this request.

        Args:
            payload: Request payload.

        Returns:
            The TV response containing authentication details.

        """
        return self._api_post_model("pair/request", PairingRequestResponse, payload)

    def pair_grant(self, payload: PairingGrantPayload) -> PairingResponse:
        """Send request finalizing the pairing process.

        This requires some data from response to request initiating the pairing:
        :func:`pair_request`.

        Args:
            payload: Request payload.

        Returns:
            The TV response containing pairing confirmation or rejection.

        """
        return self._api_post_model("pair/grant", PairingResponse, payload)

    def get_powerstate(self) -> PowerState:
        """Send request to get the current power state."""
        return self._api_get_model("powerstate", PowerState)

    def set_powerstate(self, powerstate: PowerState) -> None:
        """Send request to set the power state."""
        self._api_post("powerstate", powerstate)

    def get_volume(self) -> CurrentVolume:
        """Send request to get the current volume, mute status, and volume limits."""
        return self._api_get_model("audio/volume", CurrentVolume)

    def set_volume(self, volume: Volume) -> None:
        """Send request to set the volume."""
        self._api_post("audio/volume", volume)

    def get_current_channel(self) -> CurrentChannel:
        """Send request to get current TV app activity."""
        return self._api_get_model("activities/tv", CurrentChannel)

    def get_all_channels(self) -> AllChannels:
        """Send request to get all available channels."""
        return self._api_get_model("channeldb/tv/channelLists/all", AllChannels)

    def set_channel(self, channel: SetChannel) -> None:
        """Send request to set the channel."""
        self._api_post("activities/tv", channel)

    def input_key(self, key: InputKey) -> None:
        """Send request to simulate pressing key on the remote."""
        self._api_post("input/key", key)

    def get_ambilight_power(self) -> AmbilightPower:
        """Send request to get Ambilight power state."""
        return self._api_get_model("ambilight/power", AmbilightPower)

    def set_ambilight_power(self, power: AmbilightPower) -> None:
        """Send request to set Ambilight power state."""
        self._api_post("ambilight/power", power)

    def get_ambilight_topology(self) -> AmbilightTopology:
        """Send request to get Ambilight topology."""
        return self._api_get_model("ambilight/topology", AmbilightTopology)

    def get_ambilight_mode(self) -> AmbilightMode:
        """Send request to get current Ambilight mode."""
        return self._api_get_model("ambilight/mode", AmbilightMode)

    def set_ambilight_mode(self, mode: AmbilightMode) -> None:
        """Send request to set ambilight mode."""
        self._api_post("ambilight/mode", mode)

    def get_ambilight_measured(self) -> AmbilightColors:
        """Send request to get measured color values from Ambilight system.

        Those are the colors taken directly from the displayed image, before processing by
        internal Ambilight algorithm.
        """
        return self._api_get_model("ambilight/measured", AmbilightColors)

    def get_ambilight_processed(self) -> AmbilightColors:
        """Send request to get processed color values from Ambilight system.

        Those are the measured values after processing by the internal Ambilight algorithm, based on
        the currently active Ambilight style.
        """
        return self._api_get_model("ambilight/processed", AmbilightColors)

    def get_ambilight_cached(self) -> AmbilightColors:
        """Send request to get cached color values from Ambilight system.

        Those are the values that were previously set by some user via API.
        """
        return self._api_get_model("ambilight/cached", AmbilightColors)

    def set_ambilight_cached(self, colors: AmbilightColorSettings) -> None:
        """Send request to set cached color values in Ambilight system.

        If those values are set, they override other Ambilight settings. This effectively just sets
        the Ambilight color.

        Note:
            The actual TV API allows sending the colors in one of the following ways:
                1. All pixels on all layers to the same color.
                2. All pixels on a single layer to the same color.
                3. Specific colors for pixels on chosen sides (left, top, etc.) of a single layer.
                4. Specific color for any pixel addressed by layer, side and index.

            This implementation allows only options 1 and 4. I have no idea what are the "layers".
            The TVs I have access to have only one. I wasn't able to find any information about it
            so I decided to ignore it. Option 3 could actually be useful, I'll consider implementing
            it, but right now the same effect can be achieved using option 4.

        All pixels which color's are not set in a given request (e.g. setting a single pixel's
        color), will keep their color.

        References:
            `Philips JointSpace API Documentation
            <http://jointspace.sourceforge.net/projectdata/documentation/jasonApi/1/doc/API-Method-ambilight-cached-POST.html>`_

        """
        self._api_post("ambilight/cached", colors)

    def get_applications(self) -> Applications:
        """Send request to get the list of installed applications."""
        return self._api_get_model("applications", Applications)

    def launch_application(self, application: ApplicationShort) -> None:
        """Send request to launch an application activity.

        Use values returned by :func:`get_applications`.

        Note:
            "Activity" means that this can go directly to a specific screen in the application.
            Unfortunately, I don't know where to get valid "activities" for specific applications.

        """
        self._api_post("activities/launch", application)

    def _api_post_model(
        self, path: str, resp_model: Type[_T], payload: Optional[APIObject] = None
    ) -> _T:
        raw_response = self._api_post(path, payload)
        with _wrap_validation_exceptions("POST", path, raw_response):
            return resp_model.parse(raw_response)

    def _api_get_model(self, path: str, response_model: Type[_T]) -> _T:
        raw_response = self._api_get(path)
        with _wrap_validation_exceptions("GET", path, raw_response):
            return response_model.parse(raw_response)

    def _api_post(self, path: str, payload: Optional[APIObject] = None) -> Any:
        with _wrap_unauthorized_exceptions(path):
            return self._tv.post(self._api_path(path), payload.dump() if payload else None)

    def _api_get(self, path: str) -> Any:
        with _wrap_unauthorized_exceptions(path):
            return self._tv.get(self._api_path(path))

    def _api_path(self, path: str) -> str:
        return f"{self.api_version}/{path}"
