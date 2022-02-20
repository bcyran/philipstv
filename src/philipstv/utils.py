import hmac
import random
import string
from base64 import b64encode
from hashlib import sha256


def create_device_id() -> str:
    return "".join(
        random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits)
        for _ in range(16)
    )


def create_signature(secret: bytes, message: bytes) -> bytes:
    return b64encode(hmac.new(secret, message, sha256).hexdigest().encode())
