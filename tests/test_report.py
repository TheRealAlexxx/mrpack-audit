import json

from mrpack_audit.audit import FileReport
from mrpack_audit.report import render_json, render_text, summarize


def _reports():
    return [
        FileReport("good.jar", "a" * 40, "Better Zombies", "btrzombies", "MIT",
                   "permissive", "https://modrinth.com/project/btrzombies"),
        FileReport("bad.zip", "b" * 40, "Tissou Pack", "tissou", "ARR",
                   "restricted", "https://modrinth.com/project/tissou"),
        FileReport("stray.jar", "c" * 40, None, None, None, "unmatched", None),
    ]


def test_summarize():
    assert summarize(_reports()) == {
        "permissive": 1, "restricted": 1, "unmatched": 1,
    }


def test_render_text_flags_problems():
    text = render_text(_reports())
    assert "Better Zombies" in text
    assert "FLAG" in text
    assert "not found on Modrinth" in text
    assert "do not redistribute without permission" in text
    assert "1 restricted" in text


def test_render_json_roundtrip():
    data = json.loads(render_json(_reports()))
    assert len(data) == 3
    assert data[0]["license_id"] == "MIT"
    assert data[2]["category"] == "unmatched"


def test_render_text_empty():
    assert render_text([]) == "No .jar or .zip files found."
