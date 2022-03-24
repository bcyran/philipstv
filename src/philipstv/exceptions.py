from typing import Any, Optional

from .model import PairingResponse


class PhilipsError(Exception):
    """Base exception for all exceptions raised by this package."""

    def __init__(self, message: str) -> None:
        super().__init__()
        self.message = message

    def __str__(self) -> str:
        return self.message


class PhilipsTVError(PhilipsError):
    """Raised if error occured during communication with the TV.

    Attributes:
        method: HTTP method of the request.
        url: URL of the request.
        status_code: HTTP status_code if response was received.

    """

    def __init__(self, method: str, url: str, status_code: Optional[int] = None) -> None:
        message = f"{method} request to {url} failed"
        if status_code:
            message += f" with status {status_code}"
        super().__init__(message)
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


class PhilipsTVAPIError(PhilipsError):
    """Raised when something goes wrong with API communication."""


class PhilipsTVAPIUnauthorizedError(PhilipsTVAPIError):
    """Raised when trying to use the API without, or with invalid credentials.

    Attributes:
        method: HTTP method of the request.
        path: Path of the request.

    """

    def __init__(self, method: str, path: str) -> None:
        super().__init__(f"Unauthorized API access: {method} {path}")
        self.method = method
        self.path = path


class PhilipsTVAPIMalformedResponseError(PhilipsTVAPIError):
    """Raised when response received from the API is unparsable into known object.

    Attributes:
        method: HTTP method of the request.
        path: Path of the request.
        response: Raw response JSON returned by the API.

    """

    def __init__(self, method: str, path: str, response: Any) -> None:
        super().__init__(f"Malformed API response: {method} {path}")
        self.method = method
        self.path = path
        self.response = response


class PhilipsTVRemoteError(PhilipsError):
    """Raised if there was some incorrect interaction with :class:`PhilipsTVRemote`.

    This can happen e.g. when trying to launch application which is not installed. This exception
    does *NOT* come from the TV. It comes from the :class:`PhilipsTVRemote` class logic.
    """
