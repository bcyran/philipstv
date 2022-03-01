from typing import List

from pydantic.fields import Field

from .base import APIObject


class ApplicationComponent(APIObject):
    """Model of application component API object."""

    package_name: str = Field(alias="packageName")
    """Application package name."""
    class_name: str = Field(alias="className")
    """Application class name."""


class ApplicationIntent(APIObject):
    """Model of application intent API object."""

    component: ApplicationComponent
    """Application component."""
    action: str
    """Action within application."""


class ApplicationShort(APIObject):
    """Model of an activity launch request body."""

    intent: ApplicationIntent
    """Definition of application intent."""


class Application(ApplicationShort):
    """Model of an application in application list response body."""

    label: str
    """Application name."""
    order: int
    """Application order."""
    id: str
    """Application ID."""
    type: str
    """Application type."""


class Applications(APIObject):
    """Model of applications list response body."""

    version: int
    """List version."""
    applications: List[Application]
    """List of application definitions."""
