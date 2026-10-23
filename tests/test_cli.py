from mrpack_audit.cli import main


def test_missing_target_is_a_clean_error(capsys):
    assert main(["/definitely/not/here.mrpack"]) == 2
    err = capsys.readouterr().err
    assert "no such file or directory: /definitely/not/here.mrpack" in err
    assert "Errno" not in err


def test_wrong_file_type_names_the_target(tmp_path, capsys):
    stray = tmp_path / "notes.txt"
    stray.write_text("not a pack")
    assert main([str(stray)]) == 2
    err = capsys.readouterr().err
    assert "must be a directory or .mrpack file" in err
