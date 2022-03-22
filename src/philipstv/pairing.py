import logging
from base64 import b64decode
from typing import Callable

from ._utils import create_signature
from .api import PhilipsTVAPI
from .exceptions import PhilipsTVPairingError
from .model import DeviceInfo, PairingAuthInfo, PairingGrantPayload, PairingRequestPayload
from .types import Credentials

LOGGER = logging.getLogger(__name__)

_SECRET = b64decode(
    "JCqdN5AcnAHgJYseUn7ER5k3qgtemfUvMRghQpTfTZq7Cvv8EPQPqfz6dDxPQPSu4gKFPWkJGw32zyASgJkHwCjU"
)


PinCallback = Callable[[], str]


class PhilipsTVPairer:
    """Encapsulates the pairing process and allows to perform it in a single call."""

    def __init__(self, api: PhilipsTVAPI, device_info: DeviceInfo) -> None:
        """
        Args:
            api: :class:`PhilipsTVAPI` instance with which pairing will be performed.
            device_info: Informations about the device which requests the pairing. This doesn't
                really seem to have any effect, besides the fact that `id` given here serves as a
                "username" and later will be the first value in the credentials tuple.
        """
        self._api: PhilipsTVAPI = api
        self.device_info = device_info

    def pair(self, pin_callback: PinCallback) -> Credentials:
        """Perfom the pairing.

        Hint:
            If the pairing is successful, this leaves the underlying :class:`PhilipsTVAPI` instance
            in authenticated state, so you don't have to set :attr:`PhilipsTVAPI.auth` with the
            received credentials.

        Args:
            pin_callback: Callback function which should return the PIN displayed on the TV
                screen as a string. It's impossible to know the PIN before requesting pairing
                so this function should be used to prompt the user for the PIN.

        Returns:
            Authentication credentials tuple. This value can be used to authenticate with the TV
            at any point in future.

        """
        self._api.auth = None
        pair_response = self._api.pair_request(self._get_request_payload())

        is_success = pair_response.error_id == "SUCCESS"
        if not (is_success and pair_response.auth_key and pair_response.timestamp):
            raise PhilipsTVPairingError(pair_response)

        pair_pin = pin_callback()

        self._api.auth = (self.device_info.id, pair_response.auth_key)
        grant_response = self._api.pair_grant(
            self._get_grant_payload(pair_pin, pair_response.timestamp)
        )

        if grant_response.error_id != "SUCCESS":
            self._api.auth = None
            raise PhilipsTVPairingError(grant_response)

        return (self.device_info.id, pair_response.auth_key)

    def _get_request_payload(self) -> PairingRequestPayload:
        return PairingRequestPayload(
            scope=["read", "write", "control"],
            device=self.device_info,
        )

    def _get_grant_payload(self, pin: str, timestamp: int) -> PairingGrantPayload:
        signature = create_signature(_SECRET, f"{timestamp}{pin}".encode()).decode()
        return PairingGrantPayload(
            auth=PairingAuthInfo(pin=pin, auth_timestamp=timestamp, auth_signature=signature),
            device=self.device_info,
        )
