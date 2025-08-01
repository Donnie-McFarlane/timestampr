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
import sys
from datetime import datetime, time
from pathlib import Path
from textwrap import dedent, shorten

# ─────────────────────────────────────────────────────────────────────────────
# Constants & helpers
# ─────────────────────────────────────────────────────────────────────────────

CONFIG_DIR  = Path.home() / ".timestampr"
CONFIG_FILE = CONFIG_DIR / "config.json"
DATE_FMT    = "%Y-%m-%d"
TIME_FMT    = "%H:%M:%S"
DEFAULT_FMT = f"{DATE_FMT} {TIME_FMT}"
MAX_PREVIEW = 50


def now() -> datetime:
    """Return the current ``datetime``."""
    return datetime.now()


def _parse_time(value: str) -> tuple[time, bool]:
    """Return (``time`` object, include_seconds) from ``value``."""
    try:
        return datetime.strptime(value, TIME_FMT).time(), True
    except ValueError:
        return datetime.strptime(value, "%H:%M").time(), False


def _seconds(t: time) -> int:
    """Return number of seconds past midnight for ``t``."""
    return t.hour * 3600 + t.minute * 60 + t.second


def _match_time(t1: time, t2: time, exact: bool) -> bool:
    """Return ``True`` if ``t1`` matches ``t2`` respecting ``exact`` seconds."""
    if exact:
        return t1 == t2
    return t1.hour == t2.hour and t1.minute == t2.minute


def _in_range(t: time, start: time, end: time, exact: bool) -> bool:
    """Return ``True`` if ``t`` is within ``start`` and ``end``."""
    if exact:
        s = _seconds(start)
        e = _seconds(end)
        v = _seconds(t)
    else:
        s = start.hour * 60 + start.minute
        e = end.hour * 60 + end.minute
        v = t.hour * 60 + t.minute
    return s <= v <= e


def load_config() -> dict:
    """Return stored configuration or an empty dict if none exists."""
    if CONFIG_FILE.exists():
        with CONFIG_FILE.open(encoding="utf-8") as fh:
            return json.load(fh)
    return {}


def save_config(cfg: dict) -> None:
    """Persist ``cfg`` to ``CONFIG_FILE``."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with CONFIG_FILE.open("w", encoding="utf-8") as fh:
        json.dump(cfg, fh, indent=2)


def prompt_notebook() -> Path:
    """Ask the user for a notebook folder path and ensure it exists."""
    path = input("provide file-path to your notebook (folder)\n> ").strip()
    nb = Path(path).expanduser().resolve()
    nb.mkdir(parents=True, exist_ok=True)
    return nb


def prompt_page() -> str:
    """Ask for a page name; generate a timestamped one if blank."""
    name = input("name of new page\n> ").strip()
    if not name:
        name = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    return name


def ensure_notebook(cfg: dict) -> Path:
    """Return the active notebook folder, prompting the user if necessary."""
    nb_path = Path(cfg.get("notebook", ""))
    if not nb_path.is_dir():
        nb_path = prompt_notebook()
        cfg["notebook"] = str(nb_path)
        save_config(cfg)
    return nb_path


def ensure_page(cfg: dict, nb_path: Path) -> Path:
    """Return the active page file path, creating it if needed."""
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
    """Append ``note_text`` to the current page with a timestamp."""
    cfg = load_config()
    nb_path = ensure_notebook(cfg)
    page_path = ensure_page(cfg, nb_path)

    ts = now()
    with page_path.open("a", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerow([
            ts.strftime(DATE_FMT),
            ts.strftime(TIME_FMT),
            note_text,
        ])

    print(
        f"stamp success: {shorten(cfg['page'], MAX_PREVIEW)} "
        f"{ts.strftime(DEFAULT_FMT)} {shorten(note_text, MAX_PREVIEW)}"
    )


def show_active() -> None:
    """Print the currently active notebook and page."""
    cfg = load_config()
    nb = cfg.get("notebook", "<unset>")
    pg = cfg.get("page", "<unset>")
    print(f"Active notebook: {nb}\nActive page: {pg}")


def change_notebook() -> None:
    """Prompt for a new notebook and make it active."""
    cfg = load_config()
    nb_path = prompt_notebook()
    cfg.update({"notebook": str(nb_path), "page": None})
    save_config(cfg)
    print(f"Notebook changed to {nb_path}")


def change_page() -> None:
    """Prompt for a new page within the active notebook."""
    cfg = load_config()
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


def tail(page_path: Path, n: int | None) -> list[tuple[str, str, str]]:
    """Return the last ``n`` rows from ``page_path`` (or all if ``n`` is ``None``)."""
    rows: list[tuple[str, str, str]] = []
    with page_path.open(newline="", encoding="utf-8") as fh:
        for date, tm, note in csv.reader(fh):
            rows.append((date, tm, note))
    return rows[-n:] if isinstance(n, int) else rows


def search_notes(term: str) -> list[tuple[str, str, str]]:
    """Return rows from the active page containing ``term``."""
    cfg = load_config()
    nb_path = ensure_notebook(cfg)
    page_path = ensure_page(cfg, nb_path)
    results: list[tuple[str, str, str]] = []
    with page_path.open(newline="", encoding="utf-8") as fh:
        for date, tm, note in csv.reader(fh):
            if term in note:
                results.append((date, tm, note))
    return results


def cmd_show(arg: str | None) -> None:
    """Display notes and timestamps from the active page."""
    cfg = load_config()
    nb_path = ensure_notebook(cfg)
    page_path = ensure_page(cfg, nb_path)

    rows: list[tuple[str, str, str]] = []
    with page_path.open(newline="", encoding="utf-8") as fh:
        rows = [(d, t, n) for d, t, n in csv.reader(fh)]

    def _print_rows(items: list[tuple[str, str, str]]) -> None:
        for d, t, n in items:
            print(f"{d} {t}  {n}")

    if arg is None or arg.lower() == "foot":
        _print_rows(rows[-10:])
        return
    if arg.lower() == "head":
        _print_rows(rows[:10])
        return
    if arg.lower() == "all":
        limit = 100
        _print_rows(rows[:limit])
        if len(rows) > limit:
            print(f"... showing first {limit} of {len(rows)}")
        return

    try:
        if "to" in arg:
            start_s, end_s = [s.strip() for s in arg.split("to", 1)]
            start = int(start_s)
            end = int(end_s)
        else:
            start = int(arg)
            end = start
    except ValueError:
        print("stamp failed: invalid index")
        return

    if start < 1 or end < 1 or start > len(rows) or end > len(rows):
        print("stamp failed: note index out of range")
        return

    if start > end:
        start, end = end, start

    for d, t, n in rows[start - 1 : end]:
        print(f"{d} {t} {n}")


def cmd_timenote(time_query: str) -> None:
    """Print notes for ``time_query``.

    ``time_query`` may be a single time (``HH:MM`` or ``HH:MM:SS``) or a
    range separated by ``to``. Seconds are matched only if explicitly supplied.
    """
    cfg = load_config()
    nb_path = ensure_notebook(cfg)
    page_path = ensure_page(cfg, nb_path)

    rows: list[tuple[datetime, str]] = []
    with page_path.open(newline="", encoding="utf-8") as fh:
        for date, tm, note in csv.reader(fh):
            rows.append((datetime.strptime(f"{date} {tm}", DEFAULT_FMT), note))

    def _closest(before_list: list[tuple[datetime, str]], after_list: list[tuple[datetime, str]]) -> None:
        if before_list:
            dt, note = max(before_list, key=lambda r: r[0])
            print(f"{dt.strftime(DEFAULT_FMT)}  {note}")
        else:
            print("no notes before")
        if after_list:
            dt, note = min(after_list, key=lambda r: r[0])
            print(f"{dt.strftime(DEFAULT_FMT)}  {note}")
        else:
            print("no notes after")

    if "to" in time_query:
        start_s, end_s = [s.strip() for s in time_query.split("to", 1)]
        start_t, s_exact = _parse_time(start_s)
        end_t, e_exact = _parse_time(end_s)
        exact = s_exact or e_exact
        matches = [
            (dt, note)
            for dt, note in rows
            if _in_range(dt.time(), start_t, end_t, exact)
        ]
        if matches:
            for dt, note in matches:
                print(f"{dt.strftime(DEFAULT_FMT)}  {note}")
            return
        before = [r for r in rows if _seconds(r[0].time()) < _seconds(start_t)]
        after = [r for r in rows if _seconds(r[0].time()) > _seconds(end_t)]
        _closest(before, after)
    else:
        t, exact = _parse_time(time_query)
        matches = [
            (dt, note)
            for dt, note in rows
            if _match_time(dt.time(), t, exact)
        ]
        if matches:
            for dt, note in matches:
                print(f"{dt.strftime(DEFAULT_FMT)}  {note}")
            return
        before = [r for r in rows if _seconds(r[0].time()) < _seconds(t)]
        after = [r for r in rows if _seconds(r[0].time()) > _seconds(t)]
        _closest(before, after)


# ─────────────────────────────────────────────────────────────────────────────
# Command‑line interface
# ─────────────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    """Return the argument parser for the ``stamp`` CLI."""
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
              show <idx>          show note(s) at index or range
              show head/foot/all  show first / last 10 notes or all (max 100)
              timenote <time>     show note(s) at <time> or within range
              search <keyword>    search notes containing <keyword>

            Examples
            --------
              stamp - analysed sample DF17 by mass-spec
              stamp show 15 to 20
              stamp show head
              stamp timenote 08:30 to 13:00
              stamp search DF17
            """
        ),
    )
    p.add_argument("cmd", nargs=argparse.REMAINDER)
    return p


def main(argv: list[str] | None = None) -> None:
    """CLI entry point used by the ``stamp`` console script."""
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
    if cmd == "newpage":
        change_page()
    elif cmd == "newnotebook":
        change_notebook()
    elif cmd == "active":
        show_active()
    elif cmd == "page":
        change_page()
    elif cmd == "notebook":
        change_notebook()
    elif cmd == "show":
        if not rest:
            print("stamp failed. e.g. of valid args: head, foot, all, 27, or 5 to 10")
            sys.exit(1)
        cmd_show(" ".join(rest))
    elif cmd == "timenote":
        if not rest:
            print("stamp failed: supply time as HH:MM OR supply range as HH:MM to HH:MM")
            sys.exit(1)
        cmd_timenote(" ".join(rest))
    elif cmd == "search":
        if not rest:
            print("stamp failed: supply search keyword")
            sys.exit(1)
        for d, t, n in search_notes(" ".join(rest)):
            print(f"{d} {t}  {n}")
    else:
        print(f"stamp failed: unknown command '{cmd}'")
        build_parser().print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
