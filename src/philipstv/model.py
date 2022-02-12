from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Type, TypeVar

_T = TypeVar("_T")


@dataclass(frozen=True)
class ApiModel:
    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def parse(cls: Type[_T], raw: Any) -> _T:
        return cls(**raw)


@dataclass(frozen=True)
class DeviceInfo(ApiModel):
    id: str
    device_name: str
    device_os: str
    app_id: str
    app_name: str
    type: str


@dataclass(frozen=True)
class PairingAuthInfo(ApiModel):
    pin: str
    auth_timestamp: int
    auth_signature: str


@dataclass(frozen=True)
class PairingRequestPayload(ApiModel):
    scope: List[str]
    device: DeviceInfo


@dataclass(frozen=True)
class PairingGrantPayload(ApiModel):
    auth: PairingAuthInfo
    device: DeviceInfo


@dataclass(frozen=True)
class PairingResponse(ApiModel):
    error_id: str
    error_text: str


@dataclass(frozen=True)
class PairingRequestResponse(PairingResponse):
    auth_key: Optional[str] = None
    timestamp: Optional[int] = None
    timeout: Optional[int] = None
