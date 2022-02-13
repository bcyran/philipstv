from abc import abstractmethod
from enum import Enum
from typing import Any, Protocol, Type, TypeVar

from pydantic import BaseModel

_SelfModel = TypeVar("_SelfModel", bound="APIModel")
_SelfAPIObject = TypeVar("_SelfAPIObject", bound="APIObject")
_SelfAPIEnum = TypeVar("_SelfAPIEnum", bound="APIEnum")


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
        return self.dict()

    @classmethod
    def parse(cls: Type[_SelfAPIObject], raw: Any) -> _SelfAPIObject:
        return cls.parse_obj(raw)


class APIEnumMeta(type(Enum), type(APIModel)):  # type: ignore [misc]
    pass


class APIEnum(APIModel, Enum, metaclass=APIEnumMeta):
    def dump(self) -> Any:
        return self.value

    @classmethod
    def parse(cls: Type[_SelfAPIEnum], raw: Any) -> _SelfAPIEnum:
        return cls(raw)
