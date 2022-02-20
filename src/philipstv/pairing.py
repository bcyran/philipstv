import logging
from base64 import b64decode
from typing import Callable

from ._interfaces import PhilipsTVPairingAPI
from ._utils import create_signature
from .exceptions import PhilipsTVPairingError
from .model import DeviceInfo, PairingAuthInfo, PairingGrantPayload, PairingRequestPayload
from .types import Credentials

LOGGER = logging.getLogger(__name__)

_SECRET = b64decode(
    "JCqdN5AcnAHgJYseUn7ER5k3qgtemfUvMRghQpTfTZq7Cvv8EPQPqfz6dDxPQPSu4gKFPWkJGw32zyASgJkHwCjU"
)


PinCallback = Callable[[], str]


class PhilipsTVPairer:
    def __init__(self, api: PhilipsTVPairingAPI, device_info: DeviceInfo) -> None:
        self._api: PhilipsTVPairingAPI = api
        self.device_info = device_info

    def pair(self, pin_callback: PinCallback) -> Credentials:
        self._api.set_auth(None)
        pair_response = self._api.pair_request(self._get_request_payload())

        is_success = pair_response.error_id == "SUCCESS"
        if not (is_success and pair_response.auth_key and pair_response.timestamp):
            raise PhilipsTVPairingError(pair_response)

        pair_pin = pin_callback()

        self._api.set_auth((self.device_info.id, pair_response.auth_key))
        grant_response = self._api.pair_grant(
            self._get_grant_payload(pair_pin, pair_response.timestamp)
        )

        if grant_response.error_id != "SUCCESS":
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
