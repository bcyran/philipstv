from abc import abstractmethod
from typing import Any, Optional, Protocol

from .model import (
    PairingGrantPayload,
    PairingRequestPayload,
    PairingRequestResponse,
    PairingResponse,
)
from .types import Credentials


class PhilipsTVInterface(Protocol):
    @abstractmethod
    def set_auth(self, auth: Optional[Credentials]) -> None:
        raise NotImplementedError

    @abstractmethod
    def post(self, path: str, payload: Any = None) -> Any:
        raise NotImplementedError

    @abstractmethod
    def get(self, path: str) -> Any:
        raise NotImplementedError


class PhilipsTVPairingAPI(Protocol):
    @abstractmethod
    def set_auth(self, auth: Optional[Credentials]) -> None:
        raise NotImplementedError

    @abstractmethod
    def pair_request(self, payload: PairingRequestPayload) -> PairingRequestResponse:
        raise NotImplementedError

    @abstractmethod
    def pair_grant(self, payload: PairingGrantPayload) -> PairingResponse:
        raise NotImplementedError
