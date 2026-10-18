"""Minimal Modrinth API client (standard library only)."""

from __future__ import annotations

import json
import urllib.parse
import urllib.request

API_BASE = "https://api.modrinth.com/v2"
USER_AGENT = "TheRealAlexxx/mrpack-audit/0.1.0"


class ModrinthClient:
    def __init__(self, base_url: str = API_BASE):
        self.base_url = base_url.rstrip("/")

    def _request(self, path: str, payload: dict | None = None):
        data = None
        headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
        if payload is not None:
            data = json.dumps(payload).encode()
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(self.base_url + path, data=data, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.load(resp)

    def lookup_hashes(self, sha1_hashes: list[str]) -> dict:
        """Map sha1 hex digests to Modrinth version records."""
        if not sha1_hashes:
            return {}
        return self._request(
            "/version_files",
            {"hashes": sorted(set(sha1_hashes)), "algorithm": "sha1"},
        )

    def get_projects(self, project_ids: set[str]) -> list[dict]:
        """Fetch project records for the given ids."""
        if not project_ids:
            return []
        ids = urllib.parse.quote(json.dumps(sorted(project_ids)))
        return self._request(f"/projects?ids={ids}")
