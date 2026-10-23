"""Command line entry point."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .audit import audit
from .modrinth import ModrinthClient
from .report import render_json, render_text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="mrpack-audit",
        description="Audit a Modrinth modpack (.mrpack) or mods folder for licence and provenance risk.",
    )
    parser.add_argument("target", help="Path to a .mrpack file or a folder of .jar/.zip files")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of a table")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit 1 if any file is restricted, unknown, or unmatched",
    )
    args = parser.parse_args(argv)

    if not Path(args.target).exists():
        print(f"error: no such file or directory: {args.target}", file=sys.stderr)
        return 2

    client = ModrinthClient()
    try:
        reports = audit(args.target, client)
    except (ValueError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(render_json(reports) if args.json else render_text(reports))

    if args.strict and any(
        r.category in {"restricted", "unknown", "unmatched"} for r in reports
    ):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
