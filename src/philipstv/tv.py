import logging
from contextlib import contextmanager
from typing import Any, Iterator, Optional
from urllib.parse import urljoin

import urllib3
from requests import HTTPError, Session
from requests.auth import HTTPDigestAuth
from urllib3.exceptions import InsecureRequestWarning

from ._interfaces import PhilipsTVInterface
from .exceptions import PhilipsTVError
from .types import Credentials

urllib3.disable_warnings(InsecureRequestWarning)  # type: ignore


_LOGGER = logging.getLogger(__name__)


@contextmanager
def _wrap_http_exceptions() -> Iterator[None]:
    try:
        yield
    except HTTPError as exc:
        status_code = None
        if exc.response is not None:
            status_code = exc.response.status_code
        raise PhilipsTVError(status_code) from exc


class PhilipsTV(PhilipsTVInterface):
    def __init__(self, host: str, port: int = 1926, auth: Optional[Credentials] = None) -> None:
        self.host = host
        self.port = port
        self.url = f"https://{self.host}:{self.port}"

        self._session = self._create_session()
        self.set_auth(auth)

    def set_auth(self, auth: Optional[Credentials]) -> None:
        self._session.auth = HTTPDigestAuth(*auth) if auth else None

    def post(self, path: str, payload: Any = None) -> Any:
        _LOGGER.debug("Request: POST %s %s", path, payload)
        with _wrap_http_exceptions():
            response = self._session.post(urljoin(self.url, path), json=payload)
            response.raise_for_status()
        response_body = response.json() if response.content else None
        _LOGGER.debug("Response: %s %s", response.status_code, response_body)
        return response_body

    def get(self, path: str) -> Any:
        _LOGGER.debug("Request: GET %s", path)
        with _wrap_http_exceptions():
            response = self._session.get(urljoin(self.url, path))
            response.raise_for_status()
        response_body = response.json() if response.content else None
        _LOGGER.debug("Response: %s %s", response.status_code, response_body)
        return response_body

    @staticmethod
    def _create_session() -> Session:
        session = Session()
        session.verify = False
        return session
