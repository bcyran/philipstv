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
        data = super().dict(by_alias=True)
        return data["__root__"] if self.__custom_root_type__ else data

    @classmethod
    def parse(cls: Type[_SelfAPIObject], raw: Any) -> _SelfAPIObject:
        return cls.parse_obj(raw)

    class Config:
        allow_population_by_field_name = True
        use_enum_values = True


class StrEnum(str, Enum):
    pass
