from enum import Enum
from typing import Any, Type, TypeVar

from pydantic import BaseModel
from pydantic import ValidationError as ValidationError  # noqa: F401 | intentional reexport

_SelfAPIObject = TypeVar("_SelfAPIObject", bound="APIObject")


class APIObject(BaseModel):
    """Base for all API objects.

    Note:
        In all :class:`APIObject` subclassess, all `attributes` are also `parameters` accepted in
        a constructor.

    """

    def dump(self) -> Any:
        """Dump the object's JSON data.

        This JSON data (usually a dict) represents a body of some API request or response.

        Returns:
            Model's JSON data.

        """
        data = super().dict(by_alias=True)
        return data["__root__"] if self.__custom_root_type__ else data

    @classmethod
    def parse(cls: Type[_SelfAPIObject], raw: Any) -> _SelfAPIObject:
        """Construct the API object from given JSON data.

        Each :class:`APIObject` can be created from JSON data (usually a dict) of some API request
        or response body.

        Args:
            raw: Request or response body JSON data.

        Returns:
            An instance of a subclass this is called on.

        Raises:
            ValidationError: if given JSON data cannot be parsed into this model.

        """
        return cls.parse_obj(raw)

    class Config:
        allow_population_by_field_name = True
        use_enum_values = True


class StrEnum(str, Enum):
    """Enum with string values."""

    pass
