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


MAX_MEMBER_BYTES = 1 << 30  # 1 GiB decompressed; real mod jars are far smaller


def hashes_for_member(zf, name: str, limit: int = MAX_MEMBER_BYTES) -> dict[str, str]:
    """Hash a zip member as a stream, refusing absurd decompressed sizes.

    Zip metadata sizes can lie, so the running total is what counts: a
    crafted member (zip bomb) must not be able to exhaust memory the way
    zf.read(name) would by inflating fully into RAM.
    """
    sha1 = hashlib.sha1()
    sha512 = hashlib.sha512()
    total = 0
    with zf.open(name) as handle:
        for chunk in iter(lambda: handle.read(_CHUNK), b""):
            total += len(chunk)
            if total > limit:
                raise ValueError(
                    f"member exceeds {limit} bytes decompressed: {name}"
                )
            sha1.update(chunk)
            sha512.update(chunk)
    return {"sha1": sha1.hexdigest(), "sha512": sha512.hexdigest()}


def hashes_for_bytes(data: bytes) -> dict[str, str]:
    """Return the sha1 and sha512 digests of an in-memory blob."""
    return {
        "sha1": hashlib.sha1(data).hexdigest(),
        "sha512": hashlib.sha512(data).hexdigest(),
    }
