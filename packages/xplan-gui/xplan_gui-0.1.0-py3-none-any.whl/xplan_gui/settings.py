import os
from functools import cached_property
from typing import Literal, Optional, TypedDict, List, Dict

from pydantic_settings import BaseSettings, SettingsConfigDict

from xplan_tools.interface.db import DBRepository

class AppSchema(TypedDict):
    type: str
    versions: List[str]

APPSCHEMAS: Dict[str, AppSchema] = {
    "XPlanung": {"type": "xplan",   "versions": ["5.4", "6.0"]},
    "XTrasse":  {"type": "xtrasse", "versions": ["2.0"]},
}

def get_appschema(schema_type: str, version: str):
    try:
        name = next(
            filter(
                lambda key: APPSCHEMAS[key]["type"] == schema_type, APPSCHEMAS.keys()
            )
        )
        if version not in APPSCHEMAS[name]["versions"]:
            raise ValueError(f"Invalid version for Appschema {name}")
    except (StopIteration, ValueError):
        return None
    else:
        return f"{name} {version}"

class Settings(BaseSettings):
    debug: bool = True

    PGUSER: Optional[str] = None
    PGPASSWORD: Optional[str] = None
    PGHOST: Optional[str] = None
    PGPORT: Optional[str] = None
    PGDATABASE: Optional[str] = None
    PGSERVICE: Optional[str] = None

    appschema: Literal["xplan", "xtrasse"]
    appschema_version: Literal["2.0", "5.4", "6.0"]
    app_port: int
    db_type: str = "postgres"  # defaulting to postgres
    app_mode: Literal["dev", "prod"] = "prod"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @cached_property
    def repo(self) -> DBRepository:
        # schema_type = get_schema_type(self.appschema)
        # if not schema_type:
        #     raise ValueError(f"Invalid appschema name: {self.appschema}")
        os.environ.update(
            self.model_dump(
                include={
                    "PGUSER",
                    "PGHOST",
                    "PGPASSWORD",
                    "PGPORT",
                    "PGDATABASE",
                    "PGSERVICE",
                },
                exclude_none=True,
            )
        )
        return DBRepository(
            "postgresql://",
            self.appschema_version,
            self.appschema,
        )


settings = Settings()
