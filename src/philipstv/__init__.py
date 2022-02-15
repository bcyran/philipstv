from .api import PhilipsTVAPI
from .api.model import DeviceInfo
from .exceptions import PhilipsError, PhilipsTVError, PhilipsTVPairingError, PhilipsTVRemoteError
from .pairing import PhilipsTVPairer
from .remote import AmbilightColor, InputKeyValue, PhilipsTVRemote
from .tv import PhilipsTV

__version__ = "0.1.0"

__all__ = [
    "AmbilightColor",
    "DeviceInfo",
    "InputKeyValue",
    "PhilipsError",
    "PhilipsTV",
    "PhilipsTVAPI",
    "PhilipsTVError",
    "PhilipsTVPairer",
    "PhilipsTVPairingError",
    "PhilipsTVRemote",
    "PhilipsTVRemoteError",
    "__version__",
]
