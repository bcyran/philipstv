from enum import Enum
from typing import Any, Type, TypeVar

from pydantic import BaseModel

_SelfAPIObject = TypeVar("_SelfAPIObject", bound="APIObject")


class APIObject(BaseModel):
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
