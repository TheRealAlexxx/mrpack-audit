import hashlib

from mrpack_audit.hashing import hashes_for, hashes_for_bytes


def test_hashes_for_bytes_known_value():
    data = b"better zombies test blob"
    h = hashes_for_bytes(data)
    assert h["sha1"] == hashlib.sha1(data).hexdigest()
    assert h["sha512"] == hashlib.sha512(data).hexdigest()


def test_hashes_for_matches_bytes(tmp_path):
    data = b"x" * (3 * 1024 * 1024 + 7)  # spans multiple read chunks
    f = tmp_path / "big.jar"
    f.write_bytes(data)
    assert hashes_for(f) == hashes_for_bytes(data)
