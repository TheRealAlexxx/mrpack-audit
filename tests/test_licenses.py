import pytest

from mrpack_audit.licenses import classify


@pytest.mark.parametrize("lid", ["MIT", "Apache-2.0", "BSD-3-Clause", "CC0-1.0", "Unlicense"])
def test_permissive(lid):
    assert classify(lid) == "permissive"


@pytest.mark.parametrize("lid", ["LGPL-3.0", "GPL-3.0", "MPL-2.0"])
def test_copyleft(lid):
    assert classify(lid) == "copyleft"


@pytest.mark.parametrize("lid", ["ARR", "All-Rights-Reserved", "LicenseRef-Custom"])
def test_restricted(lid):
    assert classify(lid) == "restricted"


@pytest.mark.parametrize("lid", [None, "", "Some-Custom-License", "CUSTOM"])
def test_unknown(lid):
    assert classify(lid) == "unknown"
