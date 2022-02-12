from dataclasses import asdict, dataclass
from typing import Any, Dict, Type, TypeVar

_T = TypeVar("_T")


@dataclass(frozen=True)
class APIModel:
    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def parse(cls: Type[_T], raw: Any) -> _T:
        return cls(**raw)
