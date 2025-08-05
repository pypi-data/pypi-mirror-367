from __future__ import annotations

from pathlib import Path

from httpx import Client
from openapi_pydantic import OpenAPI
from typer import Typer

from apitools import process
from apitools.config import OpenApiUrl, load_config

app = Typer()
config = load_config()


@app.command("fetch", help="fetch the latest openapi.json")
def fetch(
    url: str | None = None,
    method: str | None = None,
    target: Path | None = None,
) -> None:
    source = (
        config.source if url is None else OpenApiUrl(url=url, method=method or "get")  # type: ignore
    )
    if source is None:
        msg = "Provide source in api-tools.toml or as argument"
        raise ValueError(msg)
    target = target or config.target
    if target is None:
        msg = "Provide target in api-tools.toml or as argument"
        raise ValueError(msg)
    client = Client(base_url=source.url, follow_redirects=True)
    match source.method:
        case "post":
            response = client.post("").text
        case "get":
            response = client.get("").text
        case _:
            msg = "methods other than post and get are not supported."
            raise ValueError(msg)
    with target.open("w") as file:
        file.write(response)


@app.command("generate", help="process the given openapi.json")
def generate(input: Path, output: Path) -> None:
    with input.open() as file:
        model = OpenAPI.model_validate_json(file.read())
        process.rename(model, config)
    with output.open("w") as file:
        file.write(
            model.model_dump_json(
                by_alias=True,
                exclude_defaults=True,
                exclude_none=True,
                exclude_unset=True,
            )
        )


@app.command("update", help="fetch the latest openapi.json and process it")
def update(
    url: str | None = None,
    method: str | None = None,
    target: Path | None = None,
) -> None:
    source = (
        config.source if url is None else OpenApiUrl(url=url, method=method or "get")  # type: ignore
    )
    if source is None:
        msg = "Provide source in api-tools.toml or as argument"
        raise ValueError(msg)
    target = target or config.target
    if target is None:
        msg = "Provide target in api-tools.toml or as argument"
        raise ValueError(msg)
    client = Client(base_url=source.url, follow_redirects=True)
    match source.method:
        case "post":
            response = client.post("").text
        case "get":
            response = client.get("").text
        case _:
            msg = "methods other than post and get are not supported."
            raise ValueError(msg)
    model = OpenAPI.model_validate_json(response)
    process.rename(model, config)
    with target.open("w") as file:
        file.write(
            model.model_dump_json(
                by_alias=True,
                exclude_defaults=True,
                exclude_none=True,
                exclude_unset=True,
            )
        )


def run() -> None:
    app()


if __name__ == "__main__":
    run()
