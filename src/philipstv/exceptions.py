from typing import Optional

from .model import PairingResponse


class PhilipsError(Exception):
    """Base exception for all exceptions raised by this package."""

    def __init__(self, message: str) -> None:
        super().__init__()
        self.message = message

    def __str__(self) -> str:
        return self.message


class PhilipsTVError(PhilipsError):
    """Raised if HTTP error occured during communication with the TV.

    Attributes:
        method: HTTP method of a request.
        path: path of a request.
        status_code: HTTP status_code that caused the exception.

    """

    def __init__(self, method: str, url: str, status_code: Optional[int] = None) -> None:
        super().__init__(f"{method} request to {url} failed with status {status_code}")
        self.method = method
        self.url = url
        self.status_code = status_code


class PhilipsTVPairingError(PhilipsError):
    """Raised if pairing process failed.

    This could happen e.g. when requesting pairing during another pairing in progress, or if
    provided PIN is incorrect.

    Attributes:
        response: Response to the pairing request, containing error details.

    """

    def __init__(self, response: PairingResponse) -> None:
        super().__init__(f"Pairing error: {response.error_id} {response.error_text}")
        self.response = response


class PhilipsTVRemoteError(PhilipsError):
    """Raised if there was some incorrect interaction with :class:`PhilipsTVRemote`.

    This can happen e.g. when trying to launch application which is not installed. This exception
    does *NOT* come from the TV. It comes from the :class:`PhilipsTVRemote` class logic.
    """
