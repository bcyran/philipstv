import hmac
import platform
import random
import string
import subprocess
from base64 import b64encode
from hashlib import sha256


def ping(host: str) -> bool:
    arg = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", arg, "1", host]
    return subprocess.call(command) == 0


def create_device_id() -> str:
    return "".join(
        random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits)
        for _ in range(16)
    )


def create_signature(secret: bytes, message: bytes) -> bytes:
    return b64encode(hmac.new(secret, message, sha256).hexdigest().encode())
