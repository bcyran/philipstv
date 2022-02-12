from dataclasses import asdict, dataclass
from typing import Any, Type, TypeVar

_T = TypeVar("_T")


@dataclass(frozen=True)
class APIModel:
    def dump(self) -> Any:
        return asdict(self)

    @classmethod
    def parse(cls: Type[_T], raw: Any) -> _T:
        return cls(**raw)
