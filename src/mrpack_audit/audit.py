"""Core audit logic: collect files, match against Modrinth, classify licences."""

from __future__ import annotations

import json
import zipfile
from dataclasses import dataclass
from pathlib import Path

from .hashing import hashes_for, hashes_for_bytes, hashes_for_member
from .licenses import classify

SCAN_SUFFIXES = (".jar", ".zip")


@dataclass
class FileReport:
    path: str
    sha1: str
    project: str | None
    project_slug: str | None
    license_id: str | None
    category: str  # permissive | copyleft | restricted | unknown | unmatched
    source_url: str | None


def collect_entries(target: str | Path) -> list[tuple[str, str, str | None]]:
    """Collect (display_path, sha1, sha512) entries from a folder or .mrpack."""
    p = Path(target)
    entries: list[tuple[str, str, str | None]] = []
    if p.is_dir():
        for f in sorted(p.rglob("*")):
            if f.is_file() and f.suffix.lower() in SCAN_SUFFIXES:
                h = hashes_for(f)
                entries.append((str(f.relative_to(p)), h["sha1"], h["sha512"]))
        return entries
    if p.suffix == ".mrpack":
        with zipfile.ZipFile(p) as z:
            names = set(z.namelist())
            indexed: set[str] = set()
            if "modrinth.index.json" in names:
                info = z.getinfo("modrinth.index.json")
                if info.file_size > 64 << 20:
                    raise ValueError(
                        f"modrinth.index.json is implausibly large: {info.file_size} bytes"
                    )
                index = json.loads(z.read("modrinth.index.json"))
                for entry in index.get("files", []):
                    file_hashes = entry.get("hashes", {})
                    sha1 = file_hashes.get("sha1")
                    if sha1:
                        indexed.add(entry.get("path"))
                        entries.append(
                            (entry.get("path"), sha1, file_hashes.get("sha512"))
                        )
            for name in sorted(names):
                if name.endswith("/") or name in indexed:
                    continue
                if name.lower().endswith(SCAN_SUFFIXES):
                    h = hashes_for_member(z, name)
                    entries.append((name, h["sha1"], h["sha512"]))
        return entries
    raise ValueError(f"target must be a directory or .mrpack file: {target}")


def audit(target: str | Path, client) -> list[FileReport]:
    """Audit a folder or .mrpack using a client with lookup_hashes/get_projects."""
    entries = collect_entries(target)
    matches = client.lookup_hashes([sha1 for _, sha1, _ in entries])
    project_ids = {m["project_id"] for m in matches.values()}
    projects = {p["id"]: p for p in client.get_projects(project_ids)}

    reports: list[FileReport] = []
    for path, sha1, _ in entries:
        version = matches.get(sha1)
        if version is None:
            reports.append(
                FileReport(path, sha1, None, None, None, "unmatched", None)
            )
            continue
        proj = projects.get(version["project_id"], {})
        lic = proj.get("license")
        lic_id = lic.get("id") if isinstance(lic, dict) else lic
        slug = proj.get("slug")
        reports.append(
            FileReport(
                path=path,
                sha1=sha1,
                project=proj.get("title"),
                project_slug=slug,
                license_id=lic_id,
                category=classify(lic_id),
                source_url=f"https://modrinth.com/project/{slug}" if slug else None,
            )
        )
    return reports
