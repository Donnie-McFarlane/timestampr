#!/usr/bin/env python3
"""
timestampr – bare‑bones, file‑based note‑taking with timestamps.

Entry‑point command:  stamp
Typical usage:        stamp - checking email
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from textwrap import dedent, shorten

# ─────────────────────────────────────────────────────────────────────────────
# Constants & helpers
# ─────────────────────────────────────────────────────────────────────────────

CONFIG_DIR   = Path.home() / ".timestampr"
CONFIG_FILE  = CONFIG_DIR / "config.json"
DEFAULT_FMT  = "%Y-%m-%d %H:%M:%S"          # timestamp format on disk
MAX_PREVIEW  = 50                           # chars shown in success message


def now() -> str:
    """Return current timestamp string in DEFAULT_FMT."""
    return datetime.now().strftime(DEFAULT_FMT)


def load_config() -> dict:
    if CONFIG_FILE.exists():
        with CONFIG_FILE.open(encoding="utf-8") as fh:
            return json.load(fh)
    return {}


def save_config(cfg: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with CONFIG_FILE.open("w", encoding="utf-8") as fh:
        json.dump(cfg, fh, indent=2)


def prompt_notebook() -> Path:
    path = input("provide file-path to your notebook (folder)\n> ").strip()
    nb   = Path(path).expanduser().resolve()
    nb.mkdir(parents=True, exist_ok=True)
    return nb


def prompt_page() -> str:
    name = input("name of new page\n> ").strip()
    if not name:
        name = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    return name


def ensure_notebook(cfg: dict) -> Path:
    nb_path = Path(cfg.get("notebook", ""))
    if not nb_path.is_dir():
        nb_path = prompt_notebook()
        cfg["notebook"] = str(nb_path)
        save_config(cfg)
    return nb_path


def ensure_page(cfg: dict, nb_path: Path) -> Path:
    page_name = cfg.get("page")
    page_path = nb_path / f"{page_name}.csv" if page_name else None
    if not page_path or not page_path.exists():
        page_name = prompt_page()
        page_path = nb_path / f"{page_name}.csv"
        page_path.touch()
        cfg["page"] = page_name
        save_config(cfg)
    return page_path


def append_note(note_text: str) -> None:
    cfg       = load_config()
    nb_path   = ensure_notebook(cfg)
    page_path = ensure_page(cfg, nb_path)

    ts = now()
    with page_path.open("a", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerow([ts, note_text])

    print(
        f"stamp success: page {shorten(cfg['page'], MAX_PREVIEW)} "
        f"timestamp {ts} note {shorten(note_text, MAX_PREVIEW)}"
    )


def show_active() -> None:
    cfg = load_config()
    nb  = cfg.get("notebook", "<unset>")
    pg  = cfg.get("page", "<unset>")
    print(f"Active notebook: {nb}\nActive page: {pg}")


def change_notebook() -> None:
    cfg      = load_config()
    nb_path  = prompt_notebook()
    cfg.update({"notebook": str(nb_path), "page": None})
    save_config(cfg)
    print(f"Notebook changed to {nb_path}")


def change_page() -> None:
    cfg     = load_config()
    nb_path = ensure_notebook(cfg)

    pages = sorted(p.stem for p in nb_path.glob("*.csv"))
    if pages:
        print("Existing pages:")
        for i, p in enumerate(pages, 1):
            print(f"[{i}] {p}")
    else:
        print("(no pages yet)")

    pg = prompt_page()
    (nb_path / f"{pg}.csv").touch()
    cfg["page"] = pg
    save_config(cfg)
    print(f"Page changed to {pg}")


def tail(page_path: Path, n: int | None) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    with page_path.open(newline="", encoding="utf-8") as fh:
        for ts, note in csv.reader(fh):
            rows.append((ts, note))
    return rows[-n:] if isinstance(n, int) else rows


def cmd_foot(n: str | None) -> None:
    cfg       = load_config()
    nb_path   = ensure_notebook(cfg)
    page_path = ensure_page(cfg, nb_path)

    if n is None:
        nrows = 10
    elif n.lower() == "all":
        nrows = None
    else:
        nrows = int(n)

    for ts, note in tail(page_path, nrows):
        print(f"{ts}  {note}")


def cmd_notetime(idx: int) -> None:
    cfg       = load_config()
    nb_path   = ensure_notebook(cfg)
    page_path = ensure_page(cfg, nb_path)
    rows      = tail(page_path, None)
    try:
        ts, _ = rows[idx - 1]
        print(ts)
    except IndexError:
        print("stamp failed: note index out of range")


def cmd_timenote(ts_query: str) -> None:
    cfg       = load_config()
    nb_path   = ensure_notebook(cfg)
    page_path = ensure_page(cfg, nb_path)

    with page_path.open(newline="", encoding="utf-8") as fh:
        for ts, note in csv.reader(fh):
            if ts.startswith(ts_query):
                print(note)
                return
    print("stamp failed: timestamp not found")


# ─────────────────────────────────────────────────────────────────────────────
# Command‑line interface
# ─────────────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="stamp",
        add_help=False,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=dedent(
            """\
            Commands
            --------
              - <note>            append <note> to active page
              newpage             create / switch page
              newnotebook         create / switch notebook
              active              show active notebook & page
              page                choose existing / new page
              notebook            choose existing / new notebook
              foot [n|all]        show last n (default 10) notes or all
              notetime <idx>      show timestamp of note #idx (1‑based)
              timenote <ts>       show note whose timestamp starts with <ts>

            Examples
            --------
              stamp - fixed bug in parser
              stamp foot 25
              stamp timenote 2025-07-30
            """
        ),
    )
    p.add_argument("cmd", nargs=argparse.REMAINDER)
    return p


def main(argv: list[str] | None = None) -> None:
    argv = argv or sys.argv[1:]
    if not argv:
        build_parser().print_help()
        sys.exit(0)

    # Leading "-" means "new note"
    if argv[0] == "-":
        if len(argv) == 1:
            print("stamp failed: no note text supplied")
            sys.exit(1)
        append_note(" ".join(argv[1:]))
        return

    cmd, *rest = argv
    if   cmd == "newpage":      change_page()
    elif cmd == "newnotebook":  change_notebook()
    elif cmd == "active":       show_active()
    elif cmd == "page":         change_page()
    elif cmd == "notebook":     change_notebook()
    elif cmd == "foot":         cmd_foot(rest[0] if rest else None)
    elif cmd == "notetime":
        if not rest:
            print("stamp failed: supply note index")
            sys.exit(1)
        cmd_notetime(int(rest[0]))
    elif cmd == "timenote":
        if not rest:
            print("stamp failed: supply timestamp prefix")
            sys.exit(1)
        cmd_timenote(rest[0])
    else:
        print(f"stamp failed: unknown command '{cmd}'")
        build_parser().print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
