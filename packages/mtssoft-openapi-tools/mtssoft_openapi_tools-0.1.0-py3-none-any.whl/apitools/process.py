from __future__ import annotations

from openapi_pydantic import OpenAPI, Operation, PathItem

from apitools.config import DeprecationPrefix, DeprecationSuffix, Method, RenameConfig


def _is_parameter(part: str) -> bool:
    return part.startswith("{") and part.endswith("}")


def _make_singular(parts: list[str], _param: str) -> None:
    if len(parts) == 0:
        return
    part = parts[-1]
    if part.endswith("s") and len(part) > 1:
        parts[-1] = part[:-1]


class _NameGenerator:
    generated: set[str]
    conflicts: set[str]
    config: RenameConfig

    def __init__(self, config: RenameConfig | None = None) -> None:
        self.generated = set()
        self.conflicts = set()
        self.config = config or RenameConfig()

    def create_name(self, method: Method, path: str, op: Operation) -> str | None:
        config = self.config.get_rename_config(path)
        if config.ignore is True:
            return None
        prefix = (config.methods or {}).get(method, method)
        path = (config.overrides or {}).get(path, path)
        parts = path.split("/")
        route: list[str] = []
        if op.deprecated and (config.deprecated is not None):
            if config.deprecated == "exclude":
                return None
            if isinstance(config.deprecated, DeprecationPrefix):
                parts = [config.deprecated.prefix, *parts]
            if isinstance(config.deprecated, DeprecationSuffix):
                parts.append(config.deprecated.suffix)
        for part in parts:
            if len(part) == 0:
                continue
            if _is_parameter(part):
                _make_singular(route, part)
                continue
            route.append(part)
        base_ident = "_".join([prefix, *route])
        new_ident = base_ident
        counter = 1
        while new_ident in self.generated:
            self.conflicts.add(base_ident)
            new_ident = f"{base_ident}_{counter}"
            counter += 1
        self.generated.add(new_ident)
        return new_ident


def _process_path(
    path: str,
    value: PathItem,
    generator: _NameGenerator,
) -> None:
    methods: list[Method] = ["post", "get", "put", "patch", "delete"]
    operations = [value.post, value.get, value.put, value.patch, value.delete]
    for idx, (method, op) in enumerate(zip(methods, operations)):
        if op is None:
            continue
        name = generator.create_name(method, path, op)
        if name is None:
            operations[idx] = None
            continue
        op.operationId = name
    (value.post, value.get, value.put, value.patch, value.delete) = operations


def rename(openapi: OpenAPI, config: RenameConfig) -> None:
    paths = openapi.paths
    components = openapi.components
    generator = _NameGenerator(config)
    if paths is None or components is None:
        return
    for path, value in paths.items():
        _process_path(path, value, generator)
