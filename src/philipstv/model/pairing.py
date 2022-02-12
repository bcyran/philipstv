from dataclasses import dataclass
from typing import List, Optional

from .base import APIDataClass


@dataclass(frozen=True)
class DeviceInfo(APIDataClass):
    id: str
    device_name: str
    device_os: str
    app_id: str
    app_name: str
    type: str


@dataclass(frozen=True)
class PairingAuthInfo(APIDataClass):
    pin: str
    auth_timestamp: int
    auth_signature: str


@dataclass(frozen=True)
class PairingRequestPayload(APIDataClass):
    scope: List[str]
    device: DeviceInfo


@dataclass(frozen=True)
class PairingGrantPayload(APIDataClass):
    auth: PairingAuthInfo
    device: DeviceInfo


@dataclass(frozen=True)
class PairingResponse(APIDataClass):
    error_id: str
    error_text: str


@dataclass(frozen=True)
class PairingRequestResponse(PairingResponse):
    auth_key: Optional[str] = None
    timestamp: Optional[int] = None
    timeout: Optional[int] = None
