class PhilipsTVAPIError(Exception):
    pass


class PairingError(Exception):
    def __init__(self, error_id: str, error_text: str) -> None:
        self.error_id = error_id
        self.error_text = error_text
        super().__init__(f"Pairing error: {error_id} {error_text}")
