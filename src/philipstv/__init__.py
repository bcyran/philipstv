from .api import PhilipsTVAPI
from .exceptions import (
    PhilipsError,
    PhilipsTVAPIError,
    PhilipsTVAPIMalformedResponseError,
    PhilipsTVAPIUnauthorizedError,
    PhilipsTVError,
    PhilipsTVPairingError,
    PhilipsTVRemoteError,
)
from .model import DeviceInfo
from .pairing import PhilipsTVPairer
from .remote import AmbilightColor, InputKeyValue, PhilipsTVRemote
from .tv import PhilipsTV

__version__ = "0.0.0"  # This will be set during build by poetry-dynamic-versioning

__all__ = [
    "AmbilightColor",
    "DeviceInfo",
    "InputKeyValue",
    "PhilipsError",
    "PhilipsTV",
    "PhilipsTVAPI",
    "PhilipsTVAPIError",
    "PhilipsTVAPIMalformedResponseError",
    "PhilipsTVAPIUnauthorizedError",
    "PhilipsTVError",
    "PhilipsTVPairer",
    "PhilipsTVPairingError",
    "PhilipsTVRemote",
    "PhilipsTVRemoteError",
    "__version__",
]
