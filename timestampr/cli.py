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
import sys  # needed for stdin detection
from datetime import datetime, time, date
from pathlib import Path
from textwrap import dedent, shorten
import re

# ─────────────────────────────────────────────────────────────────────────────
# Constants & helpers
# ─────────────────────────────────────────────────────────────────────────────

CONFIG_DIR  = Path.home() / ".timestampr"
CONFIG_FILE = CONFIG_DIR / "config.json"
DATE_FMT    = "%Y-%m-%d"
TIME_FMT    = "%H:%M:%S"
DEFAULT_FMT = f"{DATE_FMT} {TIME_FMT}"
MAX_PREVIEW = 50

# Time format constants
TWELVE_FMT  = "%I:%M:%S.%p"


def _read_note_from_stdin_or_prompt() -> str:
    """
    Read a note without shell parsing issues:
    - If stdin is piped, read it entirely (strip trailing newline).
    - Otherwise prompt for a single line.
    """
    try:
        is_tty = sys.stdin.isatty()
    except Exception:
        is_tty = True
    if not is_tty:
        return sys.stdin.read().rstrip("\n")
    return input("note> ")

def now() -> datetime:
    """Return the current ``datetime``."""
    return datetime.now()


def _time_from_any(value: str) -> time:
    """Return a ``time`` parsed from 12h or 24h formats."""
    value = value.strip().upper().replace(".", "")
    for fmt in ("%H:%M:%S", "%H:%M", "%I:%M:%S%p", "%I:%M%p"):
        try:
            return datetime.strptime(value, fmt).time()
        except ValueError:
            continue
    raise ValueError("invalid time format")


def _to_12h(t: time) -> str:
    """Return ``t`` formatted as ``HH:MM:SS.AM``."""
    return t.strftime(TWELVE_FMT)


def _to_24h(t: time) -> str:
    """Return ``t`` formatted as ``HH:MM:SS``."""
    return t.strftime(TIME_FMT)


def _parse_input(value: str) -> tuple[date | None, time | None]:
    """Parse ``value`` extracting optional date and time."""
    date_pat = re.compile(r"\d{4}[-/]\d{2}[-/]\d{2}")
    time_pat = re.compile(r"\d{1,2}:\d{2}(?::\d{2})?(?:\.[AP]M)?", re.IGNORECASE)
    d_match = date_pat.search(value)
    t_match = time_pat.search(value)
    d = None
    if d_match:
        d_str = d_match.group().replace("/", "-")
        d = datetime.strptime(d_str, DATE_FMT).date()
    t = _time_from_any(t_match.group()) if t_match else None
    return d, t


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

    # ensure note is single line
    note_text = note_text.replace("\n", " ").replace("\r", " ")

    ts = now()
    # determine next index
    idx = 1
    if page_path.stat().st_size > 0:
        with page_path.open(newline="", encoding="utf-8") as fh:
            idx = sum(1 for _ in csv.reader(fh)) + 1
    with page_path.open("a", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerow([
            idx,
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
    log_count = 0
    nb_path = Path(nb) if nb != "<unset>" else None
    if nb_path and pg != "<unset>":
        page_path = nb_path / f"{pg}.csv"
        if page_path.exists():
            with page_path.open(newline="", encoding="utf-8") as fh:
                log_count = sum(1 for _ in csv.reader(fh))
    print(f"Active notebook: {nb}\nActive page: {pg}\nTotal logs: {log_count}")


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


def tail(page_path: Path, n: int | None) -> list[tuple[str, str, str, str]]:
    """Return the last ``n`` rows from ``page_path`` (or all if ``n`` is ``None``)."""
    rows: list[tuple[str, str, str, str]] = []
    with page_path.open(newline="", encoding="utf-8") as fh:
        for idx, date, tm, note in csv.reader(fh):
            rows.append((idx, date, tm, note))
    return rows[-n:] if isinstance(n, int) else rows


def search_notes(term: str) -> list[tuple[str, str, str, str]]:
    """Return rows from the active page containing ``term`` (case-insensitive)."""
    cfg = load_config()
    nb_path = ensure_notebook(cfg)
    page_path = ensure_page(cfg, nb_path)
    results: list[tuple[str, str, str, str]] = []
    term_l = term.lower()
    with page_path.open(newline="", encoding="utf-8") as fh:
        for idx, d, tm, note in csv.reader(fh):
            if term_l in note.lower():
                results.append((idx, d, tm, note))
    return results


def cmd_show(arg: str | None) -> None:
    """Display notes and timestamps from the active page."""
    cfg = load_config()
    nb_path = ensure_notebook(cfg)
    page_path = ensure_page(cfg, nb_path)

    rows: list[tuple[str, str, str, str]] = []
    with page_path.open(newline="", encoding="utf-8") as fh:
        rows = [(i, d, t, n) for i, d, t, n in csv.reader(fh)]

    def _print_rows(items: list[tuple[str, str, str, str]]) -> None:
        for i, d, t, n in items:
            print(f"{i} {d} {t}  {n}")

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
    if arg.lower() == "first":
        if rows:
            _print_rows(rows[:1])
        return
    if arg.lower() == "last":
        if rows:
            _print_rows(rows[-1:])
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

    for i, d, t, n in rows[start - 1 : end]:
        print(f"{i} {d} {t} {n}")


def cmd_times(query: str) -> None:
    """Print notes based on ``query`` with optional date/time range."""
    cfg = load_config()
    nb_path = ensure_notebook(cfg)
    page_path = ensure_page(cfg, nb_path)

    rows: list[tuple[int, datetime, str, str, str]] = []
    with page_path.open(newline="", encoding="utf-8") as fh:
        for idx, d, tm, note in csv.reader(fh):
            dt = datetime.combine(
                datetime.strptime(d, DATE_FMT).date(),
                _time_from_any(tm)
            )
            rows.append((int(idx), dt, d, tm, note))

    # split query into from / to parts
    if " to " in query:
        from_s, to_s = [s.strip() for s in query.split(" to ", 1)]
    elif " - " in query:
        from_s, to_s = [s.strip() for s in query.split(" - ", 1)]
    else:
        parts = query.split(" to ")
        from_s = query.strip()
        to_s = None

    from_d, from_t = _parse_input(from_s)
    to_d = to_t = None
    if to_s:
        to_d, to_t = _parse_input(to_s)

    today = datetime.now().date()
    if to_s:
        if from_d and not to_d:
            to_d = from_d
        if to_d and not from_d:
            from_d = to_d
        if from_d is None:
            from_d = today
        if to_d is None:
            to_d = from_d
        if from_t is None:
            from_t = time(0, 0)
        if to_t is None:
            to_t = time(23, 59, 59)
        start_dt = datetime.combine(from_d, from_t)
        end_dt = datetime.combine(to_d, to_t)
        matches = [r for r in rows if start_dt <= r[1] <= end_dt]
        for i, dt, d, tm, note in matches:
            print(f"{i} {d} {tm}  {note}")
        return

    # only from_s
    d = from_d or today
    if from_t is None:
        for i, dt, d_, tm, note in rows:
            if dt.date() == d:
                print(f"{i} {d_} {tm}  {note}")
        return
    search_dt = datetime.combine(d, from_t)
    matches = [r for r in rows if r[1] == search_dt]
    if len(matches) == 1:
        i, dt, d_, tm, note = matches[0]
        print(f"{i} {d_} {tm}  {note}")
        return
    before = [r for r in rows if r[1] < search_dt]
    after = [r for r in rows if r[1] > search_dt]
    if before:
        b = max(before, key=lambda r: r[1])
        print(f"BEFORE {b[0]} {b[2]} {b[3]}  {b[4]}")
    if after:
        a = min(after, key=lambda r: r[1])
        print(f"AFTER {a[0]} {a[2]} {a[3]}  {a[4]}")


def cmd_clock(fmt: str) -> None:
    """Convert all times in the active page to ``fmt`` (``12h`` or ``24h``)."""
    fmt = fmt.lower()
    if fmt not in {"12h", "24h"}:
        print("stamp failed: clock requires '12h' or '24h'")
        return
    cfg = load_config()
    nb_path = ensure_notebook(cfg)
    page_path = ensure_page(cfg, nb_path)
    rows: list[list[str]] = []
    with page_path.open(newline="", encoding="utf-8") as fh:
        for idx, d, tm, note in csv.reader(fh):
            t_obj = _time_from_any(tm)
            tm_new = _to_12h(t_obj) if fmt == "12h" else _to_24h(t_obj)
            rows.append([idx, d, tm_new, note])
    with page_path.open("w", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerows(rows)


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
              active              show active notebook & page
              page                choose existing / new page
              notebook            choose existing / new notebook
              show <idx>          show note(s) at index or within range <M to N>
              show head/foot/all  show first / last 10 notes or all (max 100)
              show first/last     show very first or very last note
              times <query>       show notes by date/time; e.g. '08:00', 'from 08:00 to 09:00'
              clock 12h|24h       convert page times to 12h or 24h format
              search <keyword>    search notes containing <keyword>
              
            Examples
            --------
              stamp - analysed sample DF17 by mass-spec
              stamp show 15 to 20
              stamp show head
              stamp times 08:30 to 13:00
              stamp search DF17
            """
        ),
    )
    p.add_argument("cmd", nargs=argparse.REMAINDER)
    return p


def show_help() -> None:
    """Display CLI usage and repository link."""
    build_parser().print_help()
    print("\nFor more info: https://github.com/Donnie-McFarlane/timestampr")


def main(argv: list[str] | None = None) -> None:
    """CLI entry point used by the ``stamp`` console script."""
    argv = argv or sys.argv[1:]
    if not argv:
        show_help()
        sys.exit(0)

    # Leading "-" means "new note"
    if argv[0] == "-":
        if len(argv) == 1:
            note_text = _read_note_from_stdin_or_prompt()
        else:
            note_text = " ".join(argv[1:])
        append_note(note_text)
        return

    cmd, *rest = argv
    if cmd in {"h", "-h", "help", "-help", "--h", "--help"}:
        show_help()
        return
    if cmd == "active":
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
    elif cmd == "times":
        if not rest:
            print("stamp failed: supply time/date query")
            sys.exit(1)
        cmd_times(" ".join(rest))
    elif cmd == "clock":
        if not rest:
            print("stamp failed: supply 12h or 24h")
            sys.exit(1)
        cmd_clock(rest[0])
    elif cmd == "search":
        if not rest:
            print("stamp failed: supply search keyword")
            sys.exit(1)
        for i, d, t, n in search_notes(" ".join(rest)):
            print(f"{i} {d} {t}  {n}")
    else:
        print(f"stamp failed: unknown command '{cmd}'")
        show_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
