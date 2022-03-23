import logging
from contextlib import contextmanager
from typing import Any, Iterator, Optional
from urllib.parse import urljoin

import urllib3
from requests import RequestException, Session
from requests.auth import HTTPDigestAuth
from urllib3.exceptions import InsecureRequestWarning

from .exceptions import PhilipsTVError
from .types import Credentials

urllib3.disable_warnings(InsecureRequestWarning)  # type: ignore


_LOGGER = logging.getLogger(__name__)


@contextmanager
def _wrap_http_exceptions() -> Iterator[None]:
    try:
        yield
    except RequestException as exc:
        status_code = exc.response.status_code if exc.response is not None else None
        raise PhilipsTVError(exc.request.method, exc.request.url, status_code) from exc


class PhilipsTV:
    """Lowest level interface with the TV.

    Used to send raw (without using model objects) `GET` and `POST` requests to any API path.

    This handles authentication, exception handling, logging and URL building so higher layers don't
    have to worry about this.
    """

    def __init__(self, host: str, port: int = 1926, auth: Optional[Credentials] = None) -> None:
        """
        Args:
            host: TV IP address to connect to.
            port: TV port to connect to.
            auth: Authentication credentials tuple.

        """
        self.host = host
        self.port = port
        self.url = f"https://{self.host}:{self.port}"

        self._auth: Optional[Credentials] = None
        self._session = self._create_session()
        self.auth = auth

    @property
    def auth(self) -> Optional[Credentials]:
        """Credentials used for authentication.

        Hint:
            This value can be set and changed at any moment during :class:`PhilipsTV` usage.

        """
        return self._auth

    @auth.setter
    def auth(self, value: Optional[Credentials]) -> None:
        self._session.auth = HTTPDigestAuth(*value) if value else None
        self._auth = value

    def post(self, path: str, payload: Any = None) -> Any:
        """Send `POST` request.

        Args:
            path: The path to send the request to.
            payload: Request payload to send.

        Returns:
            The TV's JSON response body or ``None``.

        """
        _LOGGER.debug("Request: POST %s %s", path, payload)
        with _wrap_http_exceptions():
            response = self._session.post(urljoin(self.url, path), json=payload)
            response.raise_for_status()
        response_body = response.json() if response.content else None
        _LOGGER.debug("Response: %s %s", response.status_code, response_body)
        return response_body

    def get(self, path: str) -> Any:
        """Send `GET` request.

        Args:
            path: The path to send the request to.

        Returns:
            The TV's JSON response body or ``None``.

        """
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
