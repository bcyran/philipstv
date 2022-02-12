from typing import Optional


class PhilipsError(Exception):
    pass


class PhilipsTVError(PhilipsError):
    def __init__(self, status_code: Optional[int] = None) -> None:
        self.status_code = status_code
        super().__init__()


class PhilipsTVPairerError(PhilipsError):
    def __init__(self, error_id: str, error_text: str) -> None:
        self.error_id = error_id
        self.error_text = error_text
        super().__init__(f"Pairing error: {error_id} {error_text}")
