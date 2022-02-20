from typing import List, Optional

from ._base import APIObject


class DeviceInfo(APIObject):
    id: str
    device_name: str
    device_os: str
    app_id: str
    app_name: str
    type: str


class PairingAuthInfo(APIObject):
    pin: str
    auth_timestamp: int
    auth_signature: str


class PairingRequestPayload(APIObject):
    scope: List[str]
    device: DeviceInfo


class PairingGrantPayload(APIObject):
    auth: PairingAuthInfo
    device: DeviceInfo


class PairingResponse(APIObject):
    error_id: str
    error_text: str


class PairingRequestResponse(PairingResponse):
    auth_key: Optional[str] = None
    timestamp: Optional[int] = None
    timeout: Optional[int] = None
