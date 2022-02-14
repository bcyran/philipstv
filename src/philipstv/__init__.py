from .api import PhilipsTVAPI
from .api.model import DeviceInfo
from .exceptions import PhilipsError, PhilipsTVError, PhilipsTVPairingError
from .pairing import PhilipsTVPairer
from .tv import PhilipsTV

__version__ = "0.1.0"

__all__ = [
    "DeviceInfo",
    "PhilipsError",
    "PhilipsTV",
    "PhilipsTVAPI",
    "PhilipsTVError",
    "PhilipsTVPairer",
    "PhilipsTVPairingError",
    "__version__",
]
