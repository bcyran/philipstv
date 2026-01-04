from typing import Any

from philipstv.exceptions import PhilipsTVError
from philipstv.tv import PhilipsTV
from philipstv.types import Credentials


class FakePhilipsTV(PhilipsTV):
    def __init__(
        self,
        post_responses: dict[str, Any] | None = None,
        get_responses: dict[str, Any] | None = None,
    ) -> None:
        self.host = ""
        self._auth: Credentials | None = None
        self.post_requests: dict[str, Any] = {}
        self.get_requests: set[str] = set()

        self.post_responses = post_responses or {}
        self.get_responses = get_responses or {}

    @property
    def auth(self) -> Credentials | None:
        return self._auth

    @auth.setter
    def auth(self, value: Credentials | None) -> None:
        self._auth = value

    def post(self, path: str, payload: Any = None) -> Any:
        self.post_requests[path] = payload
        try:
            return self._raise_or_return(self.post_responses[path])
        except KeyError as err:
            raise PhilipsTVError("POST", path, 404) from err

    def get(self, path: str) -> Any:
        self.get_requests.add(path)
        try:
            return self._raise_or_return(self.get_responses[path])
        except KeyError as err:
            raise PhilipsTVError("GET", path, 404) from err

    @staticmethod
    def _raise_or_return(value: Any) -> Any:
        if isinstance(value, Exception):
            raise value
        return value
