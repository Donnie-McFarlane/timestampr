from pathlib import Path
import sys
from datetime import datetime
import builtins
import csv

import pytest

import timestampr.cli as cli

@pytest.fixture(autouse=True)
def temp_cfg(tmp_path, monkeypatch):
    cfg_dir = tmp_path / "cfg"
    cfg_file = cfg_dir / "config.json"
    monkeypatch.setattr(cli, "CONFIG_DIR", cfg_dir)
    monkeypatch.setattr(cli, "CONFIG_FILE", cfg_file)
    yield

def _fake_input(value):
    return lambda _: value

@pytest.mark.parametrize("_", range(3))
def test_now(_):
    ts = cli.now()
    assert isinstance(ts, datetime)
    assert ts.strftime(cli.DEFAULT_FMT)

@pytest.mark.parametrize("data", [{}, {"a": 1}, {"foo": "bar"}])
def test_load_save_config(tmp_path, monkeypatch, data):
    monkeypatch.setattr(cli, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(cli, "CONFIG_FILE", tmp_path / "c.json")
    cli.save_config(data)
    assert cli.load_config() == data

@pytest.mark.parametrize("name", ["nb1", "path/nb2", "spaced nb"])
def test_prompt_notebook(tmp_path, monkeypatch, name):
    monkeypatch.setattr(builtins, "input", _fake_input(str(tmp_path / name)))
    nb = cli.prompt_notebook()
    assert nb.is_dir()

@pytest.mark.parametrize("value", ["page1", " spaced ", ""])
def test_prompt_page(monkeypatch, value):
    monkeypatch.setattr(builtins, "input", _fake_input(value))
    result = cli.prompt_page()
    if value.strip():
        assert result == value.strip()
    else:
        assert result.endswith("_" + result.split("_")[-1])

@pytest.mark.parametrize("missing", [True, False, None])
def test_ensure_notebook(tmp_path, monkeypatch, missing):
    cfg = {}
    if missing is False:
        nb = tmp_path / "nb"
        nb.mkdir()
        cfg["notebook"] = str(nb)
    elif missing:
        cfg["notebook"] = str(tmp_path / "missing")
    def fake_prompt():
        path = tmp_path / "newnb"
        path.mkdir(exist_ok=True)
        return path
    monkeypatch.setattr(cli, "prompt_notebook", fake_prompt)
    nb_path = cli.ensure_notebook(cfg)
    assert nb_path.is_dir()

@pytest.mark.parametrize("missing", [True, False, None])
def test_ensure_page(tmp_path, monkeypatch, missing):
    nb = tmp_path
    cfg = {}
    if missing is False:
        page = nb / "page.csv"
        page.touch()
        cfg["page"] = "page"
    elif missing:
        cfg["page"] = "missing"
    monkeypatch.setattr(cli, "prompt_page", lambda: "newpage")
    page_path = cli.ensure_page(cfg, nb)
    assert page_path.exists()

@pytest.mark.parametrize("_", range(3))
def test_append_note(tmp_path, monkeypatch, _):
    cfg = {"notebook": str(tmp_path), "page": "p"}
    (tmp_path / "p.csv").touch()
    monkeypatch.setattr(cli, "load_config", lambda: cfg)
    monkeypatch.setattr(cli, "save_config", lambda c: None)
    cli.append_note("test")
    rows = list(csv.reader(open(tmp_path / "p.csv")))
    assert rows[-1][2] == "test"

@pytest.mark.parametrize("_", range(3))
def test_tail(tmp_path, _):
    path = tmp_path / "a.csv"
    with path.open("w", newline="") as fh:
        writer = csv.writer(fh)
        for i in range(5):
            writer.writerow([f"d{i}", f"t{i}", f"n{i}"])
    assert len(cli.tail(path, 2)) == 2
    assert len(cli.tail(path, None)) == 5


@pytest.mark.parametrize("_", range(3))
def test_show_active(monkeypatch, capsys, _):
    monkeypatch.setattr(cli, "load_config", lambda: {"notebook": "nb", "page": "pg"})
    cli.show_active()
    captured = capsys.readouterr().out
    assert "nb" in captured and "pg" in captured

@pytest.mark.parametrize("_", range(3))
def test_change_notebook(tmp_path, monkeypatch, _):
    cfg = {}
    monkeypatch.setattr(cli, "load_config", lambda: cfg)
    monkeypatch.setattr(builtins, "input", _fake_input(str(tmp_path / "newnb")))
    cli.change_notebook()
    assert cfg["notebook"] == str((tmp_path / "newnb").resolve())

@pytest.mark.parametrize("_", range(3))
def test_change_page(tmp_path, monkeypatch, _):
    cfg = {"notebook": str(tmp_path)}
    monkeypatch.setattr(cli, "load_config", lambda: cfg)
    monkeypatch.setattr(cli, "ensure_notebook", lambda c: Path(cfg["notebook"]))
    monkeypatch.setattr(builtins, "input", _fake_input("pg"))
    cli.change_page()
    assert cfg["page"] == "pg"

@pytest.mark.parametrize("_", range(3))
def test_cmd_show_keywords(tmp_path, monkeypatch, capsys, _):
    page = tmp_path / "notes.csv"
    with page.open("w", newline="") as fh:
        w = csv.writer(fh)
        for i in range(15):
            w.writerow([f"d{i}", f"t{i}", f"n{i}"])
    monkeypatch.setattr(cli, "load_config", lambda: {})
    monkeypatch.setattr(cli, "ensure_notebook", lambda c: tmp_path)
    monkeypatch.setattr(cli, "ensure_page", lambda c, nb: page)
    cli.cmd_show("head")
    out = capsys.readouterr().out
    assert "n0" in out and "n10" not in out
    cli.cmd_show("foot")
    out = capsys.readouterr().out
    assert "n14" in out and "n4" not in out
    cli.cmd_show("all")
    out = capsys.readouterr().out
    assert "n0" in out and "n14" in out

@pytest.mark.parametrize("_", range(3))
def test_cmd_show_indices(tmp_path, monkeypatch, capsys, _):
    page = tmp_path / "notes.csv"
    with page.open("w", newline="") as fh:
        w = csv.writer(fh)
        for i in range(5):
            w.writerow([f"d{i}", f"t{i}", f"n{i}"])
    monkeypatch.setattr(cli, "load_config", lambda: {})
    monkeypatch.setattr(cli, "ensure_notebook", lambda c: tmp_path)
    monkeypatch.setattr(cli, "ensure_page", lambda c, nb: page)
    cli.cmd_show("2")
    assert "t1" in capsys.readouterr().out
    cli.cmd_show("2 to 4")
    out = capsys.readouterr().out
    assert "t1" in out and "t3" in out

@pytest.mark.parametrize("_", range(3))
def test_cmd_timenote(tmp_path, monkeypatch, capsys, _):
    monkeypatch.setattr(cli, "load_config", lambda: {})
    monkeypatch.setattr(cli, "ensure_notebook", lambda c: tmp_path)
    page = tmp_path / "notes.csv"
    page.write_text("2025-01-01,08:30:00,note\n")
    monkeypatch.setattr(cli, "ensure_page", lambda c, nb: page)
    cli.cmd_timenote("08:30")
    assert "note" in capsys.readouterr().out

@pytest.mark.parametrize("_", range(3))
def test_search_notes(tmp_path, monkeypatch, _):
    cfg = {"notebook": str(tmp_path), "page": "p"}
    f = tmp_path / "p.csv"
    f.write_text("2025-01-01,08:00:00,alpha\n2025-01-01,09:00:00,beta\n")
    monkeypatch.setattr(cli, "load_config", lambda: cfg)
    monkeypatch.setattr(cli, "save_config", lambda c: None)
    results = cli.search_notes("beta")
    assert results == [("2025-01-01", "09:00:00", "beta")]

@pytest.mark.parametrize("_", range(3))
def test_build_parser(_):
    p = cli.build_parser()
    assert isinstance(p, cli.argparse.ArgumentParser)

@pytest.mark.parametrize("_", range(3))
def test_main_help(monkeypatch, capsys, _):
    monkeypatch.setattr(sys, "argv", ["prog"])
    with pytest.raises(SystemExit):
        cli.main()
    assert "Commands" in capsys.readouterr().out
