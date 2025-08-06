from __future__ import annotations

from importlib import metadata as importlib_metadata

from .compare import compare


def get_version() -> str:
    try:
        return importlib_metadata.version(__name__)
    except importlib_metadata.PackageNotFoundError:
        return "unknown"


version: str = get_version()
