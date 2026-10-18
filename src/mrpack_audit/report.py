"""Render audit reports as text or JSON."""

from __future__ import annotations

import json
from dataclasses import asdict

from .audit import FileReport

_STATUS = {
    "permissive": "ok",
    "copyleft": "ok*",
    "restricted": "FLAG",
    "unknown": "check",
    "unmatched": "check",
}


def render_text(reports: list[FileReport]) -> str:
    if not reports:
        return "No .jar or .zip files found."
    widths = {
        "path": max(len(r.path) for r in reports + [FileReport("FILE", "", None, None, None, "", None)]),
        "project": max(len(r.project or "-") for r in reports + [FileReport("", "", "PROJECT", None, None, "", None)]),
        "license": max(len(r.license_id or "-") for r in reports + [FileReport("", "", None, None, "LICENSE", "", None)]),
    }
    lines = [
        f"{'FILE':<{widths['path']}}  {'PROJECT':<{widths['project']}}  {'LICENSE':<{widths['license']}}  STATUS",
        f"{'-' * widths['path']}  {'-' * widths['project']}  {'-' * widths['license']}  ------",
    ]
    for r in reports:
        lines.append(
            f"{r.path:<{widths['path']}}  {(r.project or '-'):<{widths['project']}}  {(r.license_id or '-'):<{widths['license']}}  {_STATUS[r.category]}"
        )
    counts = summarize(reports)
    lines.append("")
    lines.append(
        "Summary: "
        + ", ".join(f"{count} {cat}" for cat, count in sorted(counts.items()))
    )
    flagged = [r for r in reports if r.category in {"restricted", "unknown", "unmatched"}]
    if flagged:
        lines.append("")
        lines.append("Needs attention:")
        for r in flagged:
            if r.category == "unmatched":
                lines.append(f"  {r.path}: not found on Modrinth, provenance unverified")
            elif r.category == "restricted":
                lines.append(f"  {r.path}: {r.project} is {r.license_id}, do not redistribute without permission")
            else:
                lines.append(f"  {r.path}: {r.project} licence '{r.license_id or 'none listed'}' needs a manual look")
    return "\n".join(lines)


def render_json(reports: list[FileReport]) -> str:
    return json.dumps([asdict(r) for r in reports], indent=2)


def summarize(reports: list[FileReport]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for r in reports:
        counts[r.category] = counts.get(r.category, 0) + 1
    return counts
