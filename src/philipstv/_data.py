import json
import logging
from pathlib import Path
from typing import Optional

from appdirs import user_data_dir
from pydantic import BaseModel, ValidationError

_LOGGER = logging.getLogger(__name__)


DATA_FILE = Path(user_data_dir("philipstv", "cyran.dev")) / "data.json"


class HostData(BaseModel):
    host: str
    id: str
    key: str


class PhilipsTVData(BaseModel):
    last_host: HostData

    @classmethod
    def load(cls) -> Optional["PhilipsTVData"]:
        try:
            _LOGGER.debug("Trying to load application data from %s", DATA_FILE)
            return cls.model_validate(json.loads(DATA_FILE.read_text()))
        except FileNotFoundError:
            _LOGGER.debug("Data file not found")
            return None
        except ValidationError:
            return None
        finally:
            _LOGGER.debug("Application data loaded successfully")

    def save(self) -> None:
        _LOGGER.debug("Saving application data to %s", DATA_FILE)
        if not DATA_FILE.exists():
            _LOGGER.debug("Data file doesn't exist, creating")
            DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
            DATA_FILE.touch()
        DATA_FILE.write_text(self.model_dump_json())
        _LOGGER.debug("Application data saved successfully")
