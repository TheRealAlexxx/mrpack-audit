"""Content hashing for mod files."""

from __future__ import annotations

import hashlib
from pathlib import Path

_CHUNK = 1 << 20  # 1 MiB


def hashes_for(path: str | Path) -> dict[str, str]:
    """Return the sha1 and sha512 digests of a file, as hex strings."""
    sha1 = hashlib.sha1()
    sha512 = hashlib.sha512()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(_CHUNK), b""):
            sha1.update(chunk)
            sha512.update(chunk)
    return {"sha1": sha1.hexdigest(), "sha512": sha512.hexdigest()}


def hashes_for_bytes(data: bytes) -> dict[str, str]:
    """Return the sha1 and sha512 digests of an in-memory blob."""
    return {
        "sha1": hashlib.sha1(data).hexdigest(),
        "sha512": hashlib.sha512(data).hexdigest(),
    }
