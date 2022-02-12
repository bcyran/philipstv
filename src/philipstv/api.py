import logging
from functools import wraps
from typing import Any, Callable, Dict, Optional, ParamSpec, TypeVar
from urllib.parse import urljoin

import urllib3
from requests import HTTPError, Session
from requests.auth import HTTPDigestAuth
from urllib3.exceptions import InsecureRequestWarning

from .exceptions import PhilipsTVAPIError
from .types import Credentials

urllib3.disable_warnings(InsecureRequestWarning)  # type: ignore


_LOGGER = logging.getLogger(__name__)


_T = TypeVar("_T")
_P = ParamSpec("_P")


def _wrap_api_exceptions(func: Callable[_P, _T]) -> Callable[_P, _T]:
    @wraps(func)
    def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _T:
        try:
            return func(*args, **kwargs)
        except HTTPError as exc:
            status_code = None
            if exc.response is not None:
                status_code = exc.response.status_code
            raise PhilipsTVAPIError(status_code) from exc

    return wrapper


class PhilipsTVAPI:
    def __init__(self, host: str, port: int = 1926, auth: Optional[Credentials] = None) -> None:
        self.host = host
        self.port = port
        self.api_version = "6"
        self.url = f"https://{self.host}:{self.port}/{self.api_version}/"

        self.set_auth(auth)
        self._session = self._create_session()

    def set_auth(self, auth: Optional[Credentials]) -> None:
        self._auth = auth

    @_wrap_api_exceptions
    def post(self, path: str, payload: Optional[Dict[str, Any]] = None) -> Any:
        _LOGGER.debug("Request: POST %s %s", path, payload)
        response = self._session.post(self._get_url(path), json=payload, auth=self._get_auth())
        response.raise_for_status()
        response_body = response.json() if response.content else None
        _LOGGER.debug("Response: %s %s", response.status_code, response_body)
        return response_body

    @_wrap_api_exceptions
    def get(self, path: str) -> Any:
        _LOGGER.debug("Request: GET %s", path)
        response = self._session.get(self._get_url(path), auth=self._get_auth())
        response.raise_for_status()
        response_body = response.json() if response.content else None
        _LOGGER.debug("Response: %s %s", response.status_code, response_body)
        return response_body

    def _get_auth(self) -> Optional[HTTPDigestAuth]:
        return HTTPDigestAuth(*self._auth) if self._auth else None

    def _get_url(self, path: str) -> str:
        return urljoin(self.url, path.lstrip("/"))

    @staticmethod
    def _create_session() -> Session:
        session = Session()
        session.verify = False
        return session
