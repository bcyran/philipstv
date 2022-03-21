from typing import Any, Dict, Optional, Set

from philipstv.exceptions import PhilipsTVError
from philipstv.tv import PhilipsTV
from philipstv.types import Credentials


class FakePhilipsTV(PhilipsTV):
    def __init__(
        self,
        post_responses: Optional[Dict[str, Any]] = None,
        get_responses: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.host = ""
        self._auth: Optional[Credentials] = None
        self.post_requests: Dict[str, Any] = {}
        self.get_requests: Set[str] = set()

        self.post_responses = post_responses or {}
        self.get_responses = get_responses or {}

    @property
    def auth(self) -> Optional[Credentials]:
        return self._auth

    @auth.setter
    def auth(self, value: Optional[Credentials]) -> None:
        self._auth = value

    def post(self, path: str, payload: Any = None) -> Any:
        self.post_requests[path] = payload
        try:
            return self._raise_or_return(self.post_responses[path])
        except KeyError:
            raise PhilipsTVError("POST", path, 404)

    def get(self, path: str) -> Any:
        self.get_requests.add(path)
        try:
            return self._raise_or_return(self.get_responses[path])
        except KeyError:
            raise PhilipsTVError("GET", path, 404)

    @staticmethod
    def _raise_or_return(value: Any) -> Any:
        if isinstance(value, Exception):
            raise value
        return value
