from abc import abstractmethod
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Protocol, Type, TypeVar

_SelfModel = TypeVar("_SelfModel", bound="APIModel")
_SelfAPIDataClass = TypeVar("_SelfAPIDataClass", bound="APIDataClass")
_SelfAPIEnum = TypeVar("_SelfAPIEnum", bound="APIEnum")


class APIModel(Protocol):
    @abstractmethod
    def dump(self) -> Any:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def parse(cls: Type[_SelfModel], raw: Any) -> _SelfModel:
        raise NotImplementedError


@dataclass(frozen=True)
class APIDataClass(APIModel):
    def dump(self) -> Any:
        return asdict(self)

    @classmethod
    def parse(cls: Type[_SelfAPIDataClass], raw: Any) -> _SelfAPIDataClass:
        return cls(**raw)


class APIEnumMeta(type(Enum), type(APIModel)):  # type: ignore [misc]
    pass


class APIEnum(APIModel, Enum, metaclass=APIEnumMeta):
    def dump(self) -> Any:
        return self.value

    @classmethod
    def parse(cls: Type[_SelfAPIEnum], raw: Any) -> _SelfAPIEnum:
        return cls(raw)
