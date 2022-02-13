from abc import abstractmethod
from enum import Enum
from typing import Any, Protocol, Type, TypeVar

from pydantic import BaseModel

_SelfModel = TypeVar("_SelfModel", bound="APIModel")
_SelfAPIObject = TypeVar("_SelfAPIObject", bound="APIObject")


class APIModel(Protocol):
    @abstractmethod
    def dump(self) -> Any:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def parse(cls: Type[_SelfModel], raw: Any) -> _SelfModel:
        raise NotImplementedError


class APIObjectMeta(type(BaseModel), type(APIModel)):  # type: ignore [misc]
    pass


class APIObject(APIModel, BaseModel, metaclass=APIObjectMeta):
    def dump(self) -> Any:
        return self.dict(by_alias=True)

    @classmethod
    def parse(cls: Type[_SelfAPIObject], raw: Any) -> _SelfAPIObject:
        return cls.parse_obj(raw)

    class Config:
        allow_population_by_field_name = True
        use_enum_values = True


class StrEnum(str, Enum):
    def __str__(self) -> str:
        return str(self.value)
