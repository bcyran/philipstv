from typing import Optional


class PhilipsTVError(Exception):
    pass


class PhilipsTVAPIError(PhilipsTVError):
    def __init__(self, status_code: Optional[int] = None) -> None:
        self.status_code = status_code
        super().__init__()


class PhilipsTVPairerError(PhilipsTVError):
    def __init__(self, error_id: str, error_text: str) -> None:
        self.error_id = error_id
        self.error_text = error_text
        super().__init__(f"Pairing error: {error_id} {error_text}")
