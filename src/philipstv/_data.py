import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from appdirs import user_data_dir
from pydantic import BaseModel, BaseSettings, ValidationError
from pydantic.env_settings import SettingsSourceCallable

_LOGGER = logging.getLogger(__name__)


DATA_FILE = Path(user_data_dir("philipstv", "cyran.dev")) / "data.json"


def json_data_source(settings: BaseSettings) -> Dict[str, Any]:
    try:
        _LOGGER.debug("Trying to load application data from %s", DATA_FILE)
        return json.loads(DATA_FILE.read_text())  # type: ignore [no-any-return]
    except FileNotFoundError:
        _LOGGER.debug("Data file not found")
        return {}
    finally:
        _LOGGER.debug("Application data loaded successfully")


class HostData(BaseModel):
    host: str
    id: str
    key: str


class PhilipsTVData(BaseSettings):
    last_host: HostData

    @classmethod
    def load(cls) -> Optional["PhilipsTVData"]:
        try:
            return cls()
        except ValidationError:
            return None

    def save(self) -> None:
        _LOGGER.debug("Saving application data to %s", DATA_FILE)
        if not DATA_FILE.exists():
            _LOGGER.debug("Data file doesn't exist, creating")
            DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
            DATA_FILE.touch()
        DATA_FILE.write_text(self.json())
        _LOGGER.debug("Application data saved successfully")

    class Config:
        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            return (init_settings, json_data_source)
