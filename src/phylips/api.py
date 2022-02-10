import logging
from functools import wraps
from typing import Any, Callable, Dict, Optional, ParamSpec, Tuple, TypeVar
from urllib.parse import urljoin

import urllib3
from requests import HTTPError, Session
from requests.auth import HTTPDigestAuth
from urllib3.exceptions import InsecureRequestWarning

from .exceptions import PhilipsTVAPIError

urllib3.disable_warnings(InsecureRequestWarning)  # type: ignore


LOGGER = logging.getLogger(__name__)

Credentials = Tuple[str, str]


T = TypeVar("T")
P = ParamSpec("P")


def wrap_api_exceptions(func: Callable[P, T]) -> Callable[P, T]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return func(*args, **kwargs)
        except HTTPError as exc:
            raise PhilipsTVAPIError() from exc

    return wrapper


class PhilipsTVAPI:
    def __init__(self, host: str, port: int = 1926, auth: Optional[Credentials] = None) -> None:
        self.host = host
        self.port = port
        self.api_version = "6"
        self.url = f"https://{self.host}:{self.port}/6/"

        self._auth = auth
        self._session = self._create_session()

    def set_auth(self, auth: Optional[Credentials]) -> None:
        self._auth = auth

    @wrap_api_exceptions
    def post(self, path: str, payload: Dict[str, Any]) -> Any:
        url = urljoin(self.url, path)
        LOGGER.debug("Request: POST %s %s", path, payload)
        response = self._session.post(url, json=payload, auth=self._get_auth())
        response.raise_for_status()
        response_body = response.json()
        LOGGER.debug("Response: %s %s", response.status_code, response_body)
        return response_body

    @wrap_api_exceptions
    def get(self, path: str) -> Any:
        url = urljoin(self.url, path)
        LOGGER.debug("Request: GET %s", path)
        response = self._session.get(url, auth=self._get_auth())
        response.raise_for_status()
        response_body = response.json()
        LOGGER.debug("Response: %s %s", response.status_code, response_body)
        return response_body

    def _get_auth(self) -> Optional[HTTPDigestAuth]:
        return HTTPDigestAuth(*self._auth) if self._auth else None

    @staticmethod
    def _create_session() -> Session:
        session = Session()
        session.verify = False
        return session
