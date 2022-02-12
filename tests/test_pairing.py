from typing import Any, Dict

import pytest

from philipstv import DeviceInfo, PhilipsTVAPI, PhilipsTVPairer, PhilipsTVPairingError
from philipstv.pairing import SECRET
from philipstv.utils import create_signature
from tests.fakes import FakePhilipsTV

DEVICE_INFO = DeviceInfo(
    id="<device_id>",
    device_name="<device_name>",
    device_os="<device_os>",
    app_id="<app_id>",
    app_name="<app_name>",
    type="<type>",
)
SIGNATURE = create_signature(SECRET, "12345<pin>".encode()).decode()

RESPONSES_HAPPY_PATH: Dict[str, Dict[str, Any]] = {
    "6/pair/request": {
        "error_id": "SUCCESS",
        "error_text": "Authorization required",
        "auth_key": "<key>",
        "timestamp": 12345,
        "timeout": 60,
    },
    "6/pair/grant": {
        "error_id": "SUCCESS",
        "error_text": "Pairing completed",
    },
}
RESPONSES_REQUEST_ERROR = {
    "6/pair/request": {
        "error_id": "CONCURRENT_PAIRING",
        "error_text": "Another pairing is in process",
    },
}
RESPONSES_CONFIRM_ERROR = {
    "6/pair/grant": {
        "error_id": "INVALID_PIN",
        "error_text": "Invalid authentication parameters",
    },
}


def test_pair_happy_path() -> None:
    fake_tv = FakePhilipsTV(RESPONSES_HAPPY_PATH)
    pairer = PhilipsTVPairer(PhilipsTVAPI(fake_tv), DEVICE_INFO)

    actual_credentials = pairer.pair(lambda: "<pin>")

    assert fake_tv.post_requests["6/pair/request"] == {
        "scope": ["read", "write", "control"],
        "device": DEVICE_INFO.dump(),
    }

    assert fake_tv.post_requests["6/pair/grant"] == {
        "auth": {
            "pin": "<pin>",
            "auth_timestamp": 12345,
            "auth_signature": SIGNATURE,
        },
        "device": DEVICE_INFO.dump(),
    }
    assert actual_credentials == ("<device_id>", "<key>")


@pytest.mark.parametrize(
    "responses, expected_message",
    [
        pytest.param(
            {**RESPONSES_HAPPY_PATH, **RESPONSES_REQUEST_ERROR},
            ".*CONCURRENT_PAIRING.*",
            id="concurrent pairing",
        ),
        pytest.param(
            {**RESPONSES_HAPPY_PATH, **RESPONSES_CONFIRM_ERROR},
            ".*INVALID_PIN.*",
            id="invalid pin",
        ),
    ],
)
def test_pair_error(responses: Dict[str, Any], expected_message: str) -> None:
    fake_tv = FakePhilipsTV(responses)
    pairer = PhilipsTVPairer(PhilipsTVAPI(fake_tv), DEVICE_INFO)

    with pytest.raises(PhilipsTVPairingError, match=expected_message):
        pairer.pair(lambda: "<pin>")
