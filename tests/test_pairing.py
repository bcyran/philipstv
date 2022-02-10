from typing import Any, Dict, Optional, Tuple

import pytest

from philipstv.exceptions import PhilipsTVAPIError, PhilipsTVPairerError
from philipstv.pairing import SECRET, DeviceSpec, PhilipsTVPairer
from philipstv.utils import create_signature

DEVICE_SPEC = DeviceSpec(
    id="<device_id>",
    device_name="<device_name>",
    device_os="<device_os>",
    app_id="<app_id>",
    app_name="<app_name>",
    type="<type>",
)
SIGNATURE = create_signature(SECRET, "12345<pin>".encode()).decode()

RESPONSES_HAPPY_PATH: Dict[str, Dict[str, Any]] = {
    "pair/request": {
        "error_id": "SUCCESS",
        "error_text": "Authorization required",
        "auth_key": "<key>",
        "timestamp": 12345,
        "timeout": 60,
    },
    "pair/grant": {
        "error_id": "SUCCESS",
        "error_text": "Pairing completed",
    },
}
RESPONSES_REQUEST_ERROR = {
    "pair/request": {
        "error_id": "CONCURRENT_PAIRING",
        "error_text": "Another pairing is in process",
    },
}
RESPONSES_CONFIRM_ERROR = {
    "pair/grant": {
        "error_id": "INVALID_PIN",
        "error_text": "Invalid authentication parameters",
    },
}


class FakePhilipsTVAPI:
    def __init__(self, responses: Dict[str, Any]) -> None:
        self.auth: Any = None
        self.responses: Dict[str, Any] = responses
        self.requests: Dict[str, Any] = {}

    def set_auth(self, auth: Optional[Tuple[str, str]]) -> None:
        self.auth = auth

    def post(self, path: str, payload: Dict[str, Any]) -> Any:
        self.requests[path] = payload
        response = self.responses.get(path)
        if response:
            return response
        raise PhilipsTVAPIError()


def test_pair_request() -> None:
    fake_api = FakePhilipsTVAPI(RESPONSES_HAPPY_PATH)
    pairer = PhilipsTVPairer(fake_api, DEVICE_SPEC)

    pairer.pair_request()

    assert fake_api.auth is None
    assert fake_api.requests["pair/request"] == {
        "scope": ["read", "write", "control"],
        "device": DEVICE_SPEC.as_dict(),
    }


def test_pair_confirm() -> None:
    fake_api = FakePhilipsTVAPI(RESPONSES_HAPPY_PATH)
    pairer = PhilipsTVPairer(fake_api, DEVICE_SPEC)

    pairer.pair_confirm("<pin>", "<key>", 12345)

    assert fake_api.auth == (DEVICE_SPEC.id, "<key>")
    assert fake_api.requests["pair/grant"] == {
        "auth": {
            "auth_AppId": "1",
            "pin": "<pin>",
            "auth_timestamp": 12345,
            "auth_signature": SIGNATURE,
        },
        "device": DEVICE_SPEC.as_dict(),
    }


def test_pair_happy_path() -> None:
    fake_api = FakePhilipsTVAPI(RESPONSES_HAPPY_PATH)
    pairer = PhilipsTVPairer(fake_api, DEVICE_SPEC)

    actual_credentials = pairer.pair(lambda: "<pin>")

    assert fake_api.requests["pair/request"] == {
        "scope": ["read", "write", "control"],
        "device": DEVICE_SPEC.as_dict(),
    }

    assert fake_api.requests["pair/grant"] == {
        "auth": {
            "auth_AppId": "1",
            "pin": "<pin>",
            "auth_timestamp": 12345,
            "auth_signature": SIGNATURE,
        },
        "device": DEVICE_SPEC.as_dict(),
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
    fake_api = FakePhilipsTVAPI(responses)
    pairer = PhilipsTVPairer(fake_api, DEVICE_SPEC)

    with pytest.raises(PhilipsTVPairerError, match=expected_message):
        pairer.pair(lambda: "<pin>")
