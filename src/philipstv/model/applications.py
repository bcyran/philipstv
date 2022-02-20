from typing import List

from pydantic.fields import Field

from ._base import APIObject


class ApplicationComponent(APIObject):
    package_name: str = Field(alias="packageName")
    class_name: str = Field(alias="className")


class ApplicationIntent(APIObject):
    component: ApplicationComponent
    action: str


class ApplicationShort(APIObject):
    intent: ApplicationIntent


class Application(ApplicationShort):
    label: str
    order: int
    id: str
    type: str


class Applications(APIObject):
    version: int
    applications: List[Application]
