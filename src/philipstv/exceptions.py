from typing import Optional

from .model import PairingResponse


class PhilipsError(Exception):
    """Base exception for all exceptions raised by this package."""


class PhilipsTVError(PhilipsError):
    """Raised if HTTP error occured during communication with the TV.

    Attributes:
        status_code: HTTP status_code that caused the exception.

    """

    def __init__(self, status_code: Optional[int] = None) -> None:
        self.status_code = status_code
        super().__init__()


class PhilipsTVPairingError(PhilipsError):
    """Raised if pairing process failed.

    This could happen e.g. when requesting pairing during another pairing in progress, or if
    provided PIN is incorrect.

    Attributes:
        response: Response to the pairing request, containing error details.

    """

    def __init__(self, response: PairingResponse) -> None:
        self.response = response
        super().__init__(f"Pairing error: {response.error_id} {response.error_text}")


class PhilipsTVRemoteError(PhilipsError):
    """Raised if there was some incorrect interaction with :class:`PhilipsTVRemote`.

    This can happen e.g. when trying to launch application which is not installed. This exception
    does *NOT* come from the TV. It comes from the :class:`PhilipsTVRemote` class logic.
    """
