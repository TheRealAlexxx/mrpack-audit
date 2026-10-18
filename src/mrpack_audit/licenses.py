"""Licence classification for redistribution risk."""

from __future__ import annotations

PERMISSIVE = {
    "MIT", "MIT-0", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC",
    "CC0-1.0", "Unlicense", "Zlib", "0BSD", "CC-BY-4.0", "CC-BY-3.0",
}

COPYLEFT = {
    "LGPL-2.1", "LGPL-3.0", "GPL-2.0", "GPL-3.0", "AGPL-3.0",
    "MPL-2.0", "EUPL-1.2", "CC-BY-SA-4.0", "CC-BY-NC-SA-4.0",
}

RESTRICTED_IDS = {"ARR", "ALL-RIGHTS-RESERVED", "ALLRIGHTSRESERVED"}


def classify(license_id: str | None) -> str:
    """Classify a licence id.

    Returns one of: permissive, copyleft, restricted, unknown.
    """
    if not license_id:
        return "unknown"
    lid = license_id.strip()
    if lid in PERMISSIVE:
        return "permissive"
    if lid in COPYLEFT:
        return "copyleft"
    if lid.upper() in RESTRICTED_IDS or lid.startswith("LicenseRef"):
        return "restricted"
    return "unknown"
