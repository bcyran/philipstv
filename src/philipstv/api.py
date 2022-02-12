from typing import Any, Optional, Type, TypeVar

from .interfaces import PhilipsTVInterface
from .model import (
    APIModel,
    PairingGrantPayload,
    PairingRequestPayload,
    PairingRequestResponse,
    PairingResponse,
    PowerState,
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
