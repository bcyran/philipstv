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

    model_config = {"populate_by_name": True, "use_enum_values": True}

    def dump(self) -> Any:
        """Dump the object's JSON data.

        This JSON data (usually a dict) represents a body of some API request or response.

        Returns:
            Model's JSON data.

        """
        return self.model_dump(by_alias=True)

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
        return cls.model_validate(raw)


class StrEnum(str, Enum):
    """Enum with string values."""

    pass
