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

try:
    # `_version` module is generated during the build.
    from philipstv._version import __version__
except ImportError:
    # Fallback for development (before building)
    __version__ = "0.0.0+dev"

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
