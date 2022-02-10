import logging
from abc import abstractmethod
from base64 import b64decode
from dataclasses import asdict, dataclass
from typing import Any, Callable, Dict, Optional, Protocol, Tuple

from .exceptions import PhilipsTVPairerError
from .types import Credentials
from .utils import create_signature

LOGGER = logging.getLogger(__name__)

SECRET = b64decode(
    "JCqdN5AcnAHgJYseUn7ER5k3qgtemfUvMRghQpTfTZq7Cvv8EPQPqfz6dDxPQPSu4gKFPWkJGw32zyASgJkHwCjU"
)


PinCallback = Callable[[], str]


class PairingAPIInterface(Protocol):
    @abstractmethod
    def set_auth(self, auth: Optional[Tuple[str, str]]) -> None:
        raise NotImplementedError

    @abstractmethod
    def post(self, path: str, payload: Dict[str, Any]) -> Any:
        raise NotImplementedError


@dataclass
class DeviceSpec:
    id: str
    device_name: str
    device_os: str
    app_id: str
    app_name: str
    type: str

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PhilipsTVPairer:
    def __init__(self, api: PairingAPIInterface, device_spec: DeviceSpec) -> None:
        self.api: PairingAPIInterface = api
        self.device_spec = device_spec

    def pair(self, pin_callback: PinCallback) -> Credentials:
        pair_response = self.pair_request()
        if pair_response["error_id"] != "SUCCESS":
            raise PhilipsTVPairerError(pair_response["error_id"], pair_response["error_text"])

        pair_pin = pin_callback()

        confirm_response = self.pair_confirm(
            pair_pin, pair_response["auth_key"], pair_response["timestamp"]
        )
        if confirm_response["error_id"] != "SUCCESS":
            raise PhilipsTVPairerError(confirm_response["error_id"], confirm_response["error_text"])

        return (self.device_spec.id, pair_response["auth_key"])

    def pair_request(self) -> Dict[str, Any]:
        LOGGER.debug("Requesting pairing")
        self.api.set_auth(None)
        payload = self._get_request_payload()
        return dict(self.api.post("pair/request", payload))

    def pair_confirm(self, pin: str, auth_key: str, timestamp: int) -> Dict[str, Any]:
        LOGGER.debug("Confirming pairing")
        self.api.set_auth((self.device_spec.id, auth_key))
        payload = self._get_confirm_payload(pin, timestamp)
        response = dict(self.api.post("pair/grant", payload))
        LOGGER.debug("Pairing successful")
        return response

    def _get_request_payload(self) -> Dict[str, Any]:
        return {
            "scope": ["read", "write", "control"],
            "device": self.device_spec.as_dict(),
        }

    def _get_confirm_payload(self, pin: str, timestamp: int) -> Dict[str, Any]:
        signature = create_signature(SECRET, f"{timestamp}{pin}".encode()).decode()
        return {
            "auth": {
                "auth_AppId": "1",
                "pin": pin,
                "auth_timestamp": timestamp,
                "auth_signature": signature,
            },
            "device": self.device_spec.as_dict(),
        }
