import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from appdirs import user_data_dir
from pydantic import BaseModel, BaseSettings, ValidationError
from pydantic.env_settings import SettingsSourceCallable

DATA_FILE = Path(user_data_dir("philipstv", "cyran.dev")) / "data.json"


def json_data_source(settings: BaseSettings) -> Dict[str, Any]:
    try:
        return json.loads(DATA_FILE.read_text())  # type: ignore [no-any-return]
    except FileNotFoundError:
        return {}


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
        if not DATA_FILE.exists():
            DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
            DATA_FILE.touch()
        DATA_FILE.write_text(self.json())

    class Config:
        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            return (init_settings, json_data_source)
