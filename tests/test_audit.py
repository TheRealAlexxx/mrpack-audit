import json
import zipfile

from mrpack_audit.audit import audit, collect_entries
from mrpack_audit.hashing import hashes_for, hashes_for_bytes


class FakeClient:
    """In-memory Modrinth stand-in."""

    def __init__(self, versions, projects):
        self.versions = versions  # sha1 -> version record
        self.projects = projects  # id -> project record

    def lookup_hashes(self, sha1_hashes):
        return {h: self.versions[h] for h in sha1_hashes if h in self.versions}

    def get_projects(self, project_ids):
        return [self.projects[i] for i in project_ids if i in self.projects]


def _jar(tmp_path, name, blob):
    f = tmp_path / name
    f.write_bytes(blob)
    return f


MIT_PROJECT = {"id": "p1", "title": "Better Zombies", "slug": "btrzombies",
               "license": {"id": "MIT"}}
ARR_PROJECT = {"id": "p2", "title": "Tissou Pack", "slug": "tissou",
               "license": {"id": "ARR"}}


def test_audit_folder_mixed(tmp_path):
    good = _jar(tmp_path, "good.jar", b"good mod bytes")
    bad = _jar(tmp_path, "bad.jar", b"all rights reserved bytes")
    stray = _jar(tmp_path, "stray.jar", b"not on modrinth")
    (tmp_path / "notes.txt").write_text("ignored")

    versions = {
        hashes_for(good)["sha1"]: {"project_id": "p1"},
        hashes_for(bad)["sha1"]: {"project_id": "p2"},
    }
    projects = {"p1": MIT_PROJECT, "p2": ARR_PROJECT}

    reports = audit(tmp_path, FakeClient(versions, projects))
    by_path = {r.path: r for r in reports}

    assert set(by_path) == {"good.jar", "bad.jar", "stray.jar"}
    assert by_path["good.jar"].category == "permissive"
    assert by_path["good.jar"].project == "Better Zombies"
    assert by_path["good.jar"].source_url == "https://modrinth.com/project/btrzombies"
    assert by_path["bad.jar"].category == "restricted"
    assert by_path["stray.jar"].category == "unmatched"
    assert by_path["stray.jar"].project is None


def test_audit_mrpack_index_and_overrides(tmp_path):
    pack = tmp_path / "pack.mrpack"
    indexed_blob = b"indexed mod bytes"
    indexed_sha1 = hashes_for_bytes(indexed_blob)["sha1"]
    override_blob = b"bundled resource pack bytes"
    index = {
        "files": [
            {"path": "mods/indexed.jar",
             "hashes": {"sha1": indexed_sha1,
                        "sha512": hashes_for_bytes(indexed_blob)["sha512"]}}
        ]
    }
    with zipfile.ZipFile(pack, "w") as z:
        z.writestr("modrinth.index.json", json.dumps(index))
        z.writestr("overrides/global_packs/required_resources/Bundled.zip", override_blob)

    versions = {
        indexed_sha1: {"project_id": "p1"},
        hashes_for_bytes(override_blob)["sha1"]: {"project_id": "p2"},
    }
    projects = {"p1": MIT_PROJECT, "p2": ARR_PROJECT}

    reports = audit(pack, FakeClient(versions, projects))
    by_path = {r.path: r for r in reports}

    assert by_path["mods/indexed.jar"].category == "permissive"
    assert by_path["overrides/global_packs/required_resources/Bundled.zip"].category == "restricted"


def test_collect_entries_rejects_bad_target(tmp_path):
    f = tmp_path / "thing.txt"
    f.write_text("hi")
    try:
        collect_entries(f)
        assert False, "should raise"
    except ValueError:
        pass
