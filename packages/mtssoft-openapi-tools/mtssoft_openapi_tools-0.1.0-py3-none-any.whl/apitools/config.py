from __future__ import annotations

from pathlib import Path
from typing import Literal

import toml
from pydantic import BaseModel

Method = Literal["post", "get", "put", "patch", "delete"]


class DeprecationSuffix(BaseModel):
    suffix: str


class DeprecationPrefix(BaseModel):
    prefix: str


class RenameConfig(BaseModel):
    methods: dict[Method, str] | None = None
    overrides: dict[str, str] | None = None
    deprecated: Literal["exclude"] | DeprecationSuffix | DeprecationPrefix | None = None
    ignore: bool | None = None
    config: dict[str, RenameConfig] | None = None

    def _inherit(self) -> None:
        if self.config is None:
            return
        for config in self.config.values():
            config.methods = config.methods or self.methods
            config.overrides = config.overrides or self.overrides
            config.deprecated = config.deprecated or self.deprecated
            config.ignore = config.ignore or self.ignore

    def get_rename_config(self, path: str) -> RenameConfig:
        out = self

        longest_match = 0
        for config_path, config in (self.config or {}).items():
            length = len(config_path)
            if path.startswith(config_path) and length > longest_match:
                longest_match = length
                sub_path = path[length:]
                out = config.get_rename_config(sub_path)
        return out


class OpenApiUrl(BaseModel):
    url: str
    method: Method = "get"


class TopLevelConfig(RenameConfig):
    source: OpenApiUrl | None = None
    target: Path | None = None


def load_config() -> TopLevelConfig:
    with Path("api-tools.toml").open() as config:
        json = toml.loads(config.read())
        return TopLevelConfig.model_validate(json)
