from typing import List, Optional

from .base import APIObject


class DeviceInfo(APIObject):
    """Model of information about device requesting pairing."""

    id: str
    """ID of the device."""
    device_name: str
    """Name of the device."""
    device_os: str
    """OS of the device."""
    app_id: str
    """ID of the application."""
    app_name: str
    """Name of the application."""
    type: str
    """Type of the application."""


class PairingAuthInfo(APIObject):
    """Model of authentication information in pairing confirmation request."""

    pin: str
    """Value of the PIN displayed on the TV."""
    auth_timestamp: int
    """Timestamp value from response to the pairing request."""
    auth_signature: str
    """HMAC signature created from the PIN value."""


class PairingRequestPayload(APIObject):
    """Model of a pairing request."""

    scope: List[str]
    """Requested permissions scope. Available options are `read`, `write`, `control`."""
    device: DeviceInfo
    """Requesting device info."""


class PairingGrantPayload(APIObject):
    """Model of pairing confirmation request."""

    auth: PairingAuthInfo
    """Authentication info."""
    device: DeviceInfo
    """Requesting device info."""


class PairingResponse(APIObject):
    """Model of response the pairing request or confirmation request.

    Note:
        Even tough there's "error" in the field names it doesn't mean an actual error occured.
        The TV communicates successful states using those fields as well.

    """

    error_id: str
    """ID of the pairing process state."""
    error_text: str
    """Description of the pairing process state."""


class PairingRequestResponse(PairingResponse):
    """Model of a response to the pairing request.

    Note:
        Even tough there's "error" in the field names it doesn't mean an actual error occured.
        The TV communicates successful states using those fields as well.

    """

    auth_key: Optional[str] = None
    """Authentication key."""
    timestamp: Optional[int] = None
    """Timestamp sent by TV."""
    timeout: Optional[int] = None
    """Timeout before the pairing is cancelled."""
