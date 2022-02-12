from typing import Any, Optional

from .interfaces import PhilipsTVInterface
from .model import (
    ApiModel,
    PairingGrantPayload,
    PairingRequestPayload,
    PairingRequestResponse,
    PairingResponse,
)
from .types import Credentials


class PhilipsTVAPI:
    def __init__(self, tv: PhilipsTVInterface) -> None:
        self._tv = tv
        self.api_version = 6

    def set_auth(self, auth: Optional[Credentials]) -> None:
        self._tv.set_auth(auth)

    def pair_request(self, payload: PairingRequestPayload) -> PairingRequestResponse:
        return PairingRequestResponse.parse(self._api_post("pair/request", payload))

    def pair_grant(self, payload: PairingGrantPayload) -> PairingResponse:
        return PairingResponse.parse(self._api_post("pair/grant", payload))

    def _api_post(self, path: str, payload: Optional[ApiModel]) -> Any:
        return self._tv.post(self._api_path(path), payload.as_dict() if payload else None)

    def _api_get(self, path: str) -> Any:
        return self._tv.get(self._api_path(path))

    def _api_path(self, path: str) -> str:
        return f"{self.api_version}/{path}"
