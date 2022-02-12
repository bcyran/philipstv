from typing import Any, Dict, Optional

import pytest
from requests_mock import Mocker

from philipstv.api import PhilipsTVAPI
from philipstv.exceptions import PhilipsTVAPIError

HOST = "192.168.0.1"
PORT = 1926
PAYLOAD = {"<key>": "<value>"}

PATHS = [
    pytest.param("api/path", f"https://{HOST}:{PORT}/6/api/path", id="no leading slash"),
    pytest.param("/api/path", f"https://{HOST}:{PORT}/6/api/path", id="leading slash present"),
]
RESPONSES = [
    pytest.param({"<resp_key>": "<resp_value>"}, id="response present"),
    pytest.param(None, id="no response"),
]


@pytest.mark.parametrize("path, expected_url", PATHS)
@pytest.mark.parametrize("expected_response", RESPONSES)
def test_api_post(
    path: str, expected_url: str, expected_response: Optional[Dict[str, Any]], requests_mock: Mocker
) -> None:
    requests_mock.post(expected_url, json=expected_response)

    api = PhilipsTVAPI(HOST, PORT)
    actual_response = api.post(path, PAYLOAD)

    assert requests_mock.last_request
    assert requests_mock.last_request.json() == PAYLOAD
    assert actual_response == expected_response


@pytest.mark.parametrize("path, expected_url", PATHS)
@pytest.mark.parametrize("expected_response", RESPONSES)
def test_api_get(
    path: str, expected_url: str, expected_response: Optional[Dict[str, Any]], requests_mock: Mocker
) -> None:
    requests_mock.get(expected_url, json=expected_response)

    api = PhilipsTVAPI(HOST, PORT)
    actual_response = api.get(path)

    assert requests_mock.last_request
    assert actual_response == expected_response


@pytest.mark.parametrize("status_code", [401, 404, 500])
def test_error(status_code: int, requests_mock: Mocker) -> None:
    path = "api/path"
    url = f"https://{HOST}:{PORT}/6/{path}"
    requests_mock.post(url, status_code=status_code)

    api = PhilipsTVAPI(HOST, PORT)

    with pytest.raises(PhilipsTVAPIError) as excinfo:
        api.post(path)

    assert excinfo.value.status_code == status_code
