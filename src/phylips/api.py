from functools import wraps
from typing import Any, Callable, Dict, Optional, ParamSpec, Tuple, TypeVar
from urllib.parse import urljoin

from requests import HTTPError, Session
from requests.auth import HTTPDigestAuth

Credentials = Tuple[str, str]


class PhilipsTVAPIError(Exception):
    pass


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
        response = self._session.post(url, json=payload, auth=self._get_auth())
        response.raise_for_status()
        return response.json()

    @wrap_api_exceptions
    def get(self, path: str) -> Any:
        url = urljoin(self.url, path)
        response = self._session.get(url, auth=self._get_auth())
        response.raise_for_status()
        return response.json()

    def _get_auth(self) -> Optional[HTTPDigestAuth]:
        return HTTPDigestAuth(*self._auth) if self._auth else None

    @staticmethod
    def _create_session() -> Session:
        session = Session()
        session.verify = False
        return session
