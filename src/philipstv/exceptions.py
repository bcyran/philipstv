from typing import Optional

from .model import PairingResponse


class PhilipsError(Exception):
    pass


class PhilipsTVError(PhilipsError):
    def __init__(self, status_code: Optional[int] = None) -> None:
        self.status_code = status_code
        super().__init__()


class PhilipsTVPairingError(PhilipsError):
    def __init__(self, response: PairingResponse) -> None:
        self.response = response
        super().__init__(f"Pairing error: {response.error_id} {response.error_text}")


class PhilipsTVRemoteError(PhilipsError):
    pass
