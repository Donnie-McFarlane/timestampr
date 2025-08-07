import io
import json
from pathlib import Path
import builtins

import pytest

from timestampr import cli


def setup_config(tmp_path: Path):
    """Prepare a temporary config and notebook/page."""
    nb = tmp_path / "notebook"
    nb.mkdir(parents=True, exist_ok=True)
    page = "testpage"
    (nb / f"{page}.csv").touch()
    cfg_dir = tmp_path / ".timestampr"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    (cfg_dir / "config.json").write_text(
        json.dumps({"notebook": str(nb), "page": page}), encoding="utf-8"
    )
    return cfg_dir, nb, page


import io


class FakeStdin(io.StringIO):
    def isatty(self):
        return False


def read_last_note(csv_path: Path) -> str:
    lines = csv_path.read_text(encoding="utf-8").splitlines()
    assert lines, "Expected at least one note row"
    import csv
    idx, date, tm, note = next(csv.reader([lines[-1]]))
    assert idx and date and tm
    return note


def test_dash_with_args_writes_note(tmp_path, monkeypatch):
    cfg_dir, nb, page = setup_config(tmp_path)
    monkeypatch.setattr(cli, "CONFIG_DIR", cfg_dir)
    monkeypatch.setattr(cli, "CONFIG_FILE", cfg_dir / "config.json")
    cli.main(["-", "a", "&", "b"])
    note = read_last_note(nb / f"{page}.csv")
    assert note == "a & b"


def test_dash_reads_stdin(tmp_path, monkeypatch):
    cfg_dir, nb, page = setup_config(tmp_path)
    monkeypatch.setattr(cli, "CONFIG_DIR", cfg_dir)
    monkeypatch.setattr(cli, "CONFIG_FILE", cfg_dir / "config.json")
    fake = FakeStdin("x & y\n")
    monkeypatch.setattr(cli.sys, "stdin", fake)
    cli.main(["-"])
    note = read_last_note(nb / f"{page}.csv")
    assert note == "x & y"


def test_dash_prompt_branch_via_helper(tmp_path, monkeypatch):
    cfg_dir, nb, page = setup_config(tmp_path)
    monkeypatch.setattr(cli, "CONFIG_DIR", cfg_dir)
    monkeypatch.setattr(cli, "CONFIG_FILE", cfg_dir / "config.json")
    monkeypatch.setattr(
        cli, "_read_note_from_stdin_or_prompt", lambda: 'note with # and , and " quotes'
    )
    cli.main(["-"])
    note = read_last_note(nb / f"{page}.csv")
    assert note == 'note with # and , and " quotes'


def test_read_note_from_stdin_or_prompt_reads_stdin(monkeypatch):
    fake = FakeStdin("foo\n")
    monkeypatch.setattr(cli.sys, "stdin", fake)
    assert cli._read_note_from_stdin_or_prompt() == "foo"


def test_read_note_from_stdin_or_prompt_prompts(monkeypatch):
    class Tty(io.StringIO):
        def isatty(self):
            return True
    monkeypatch.setattr(cli.sys, "stdin", Tty())
    monkeypatch.setattr(builtins, "input", lambda _: "bar")
    assert cli._read_note_from_stdin_or_prompt() == "bar"
