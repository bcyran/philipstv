from unittest.mock import create_autospec

import pytest

from philipstv import DeviceInfo, PhilipsTVAPI, PhilipsTVPairer, PhilipsTVPairingError
from philipstv._utils import create_signature
from philipstv.model import (
    PairingAuthInfo,
    PairingGrantPayload,
    PairingRequestPayload,
    PairingRequestResponse,
    PairingResponse,
)
from philipstv.pairing import _SECRET

DEVICE_INFO = DeviceInfo(
    id="<device_id>",
    device_name="<device_name>",
    device_os="<device_os>",
    app_id="<app_id>",
    app_name="<app_name>",
    type="<type>",
)
SIGNATURE = create_signature(_SECRET, "12345<pin>".encode()).decode()
REQUEST_REPONSE_OK = PairingRequestResponse(
    error_id="SUCCESS",
    error_text="Authorization required",
    auth_key="<key>",
    timestamp=12345,
    timeout=60,
)
GRANT_RESPONSE_OK = PairingResponse(
    error_id="SUCCESS",
    error_text="Pairing completed",
)
REQUEST_REPONSE_ERR = PairingResponse(
    error_id="CONCURRENT_PAIRING",
    error_text="Another pairing is in process",
)
GRANT_RESPONSE_ERR = PairingResponse(
    error_id="INVALID_PIN",
    error_text="Invalid authentication parameters",
)


def test_pair_happy_path() -> None:
    api_mock = create_autospec(PhilipsTVAPI)
    api_mock.pair_request.return_value = REQUEST_REPONSE_OK
    api_mock.pair_grant.return_value = GRANT_RESPONSE_OK
    expected_credentials = ("<device_id>", "<key>")

    credentials = PhilipsTVPairer(api_mock, DEVICE_INFO).pair(lambda: "<pin>")

    api_mock.pair_request.assert_called_once_with(
        PairingRequestPayload(scope=["read", "write", "control"], device=DEVICE_INFO)
    )
    api_mock.pair_grant.assert_called_once_with(
        PairingGrantPayload(
            auth=PairingAuthInfo(pin="<pin>", auth_timestamp=12345, auth_signature=SIGNATURE),
            device=DEVICE_INFO,
        )
    )
    assert credentials == expected_credentials
    assert api_mock.auth == expected_credentials


@pytest.mark.parametrize(
    "pair_response, grant_response, expected_message",
    [
        (REQUEST_REPONSE_ERR, GRANT_RESPONSE_OK, ".*CONCURRENT_PAIRING.*"),
        (REQUEST_REPONSE_OK, GRANT_RESPONSE_ERR, ".*INVALID_PIN.*"),
    ],
)
def test_pair_error(
    pair_response: PairingResponse, grant_response: PairingResponse, expected_message: str
) -> None:
    api_mock = create_autospec(PhilipsTVAPI)
    api_mock.pair_request.return_value = pair_response
    api_mock.pair_grant.return_value = grant_response
    pairer = PhilipsTVPairer(api_mock, DEVICE_INFO)

    with pytest.raises(PhilipsTVPairingError, match=expected_message):
        pairer.pair(lambda: "<pin>")

    assert api_mock.auth is None
