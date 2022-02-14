from typing import Any, Dict, Optional, Set

from philipstv.exceptions import PhilipsTVError
from philipstv.interfaces import PhilipsTVInterface
from philipstv.types import Credentials


class FakePhilipsTV(PhilipsTVInterface):
    def __init__(
        self,
        post_responses: Optional[Dict[str, Any]] = None,
        get_responses: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.auth: Optional[Credentials] = None
        self.post_requests: Dict[str, Any] = {}
        self.get_requests: Set[str] = set()

        self.post_responses = post_responses or {}
        self.get_responses = get_responses or {}

    def set_auth(self, auth: Optional[Credentials]) -> None:
        self.auth = auth

    def post(self, path: str, payload: Any = None) -> Any:
        self.post_requests[path] = payload
        try:
            return self.post_responses[path]
        except KeyError:
            raise PhilipsTVError(404)

    def get(self, path: str) -> Any:
        self.get_requests.add(path)
        try:
            return self.get_responses[path]
        except KeyError:
            raise PhilipsTVError(404)
