# README.md

# timestampr

Bare-bones note-taker with timestamps – *"folder = notebook, file = page, row = note + timestamp"*

```
bash
pip install git+https://github.com/<user>/timestampr.git   # or clone & `pip install .`
stamp - writing my first note
```

---

## 1 What it does

`timestampr` lets you jot ultra-quick notes from any terminal.\
Each notebook is just a folder on your disk; each page is a `.csv` file inside that folder; every line is:

```
YYYY-MM-DD HH:MM:SS,Your note text…
```

Because it is plain text you can back-up, grep, sync to the cloud, or open in Excel.

---

## 2 Quick start

```
bash
# 1. pick or create a folder for your notebook
stamp newnotebook              # will ask for the path

# 2. pick or create a page
stamp newpage                  # name it or press <Enter> for an auto-dated page

# 3. write notes
stamp - fixed issue #42
stamp - switched buffer to CSV
```

---

## 3 All commands

| Action                                      | Command & arguments                                   |
| ------------------------------------------- | ----------------------------------------------------- |
| **New note**                                | `stamp - <note text>`                                 |
| **New page (prompt)**                       | `stamp newpage`                                       |
| **New notebook (prompt)**                   | `stamp newnotebook`                                   |
| **Show active notebook & page**             | `stamp active`                                        |
| **Change page**                             | `stamp page`                                          |
| **Change notebook**                         | `stamp notebook`                                      |
| **Show last 10 notes**                      | `stamp foot`                                          |
| **Show last *****N***** notes**             | `stamp foot N` (e.g. `stamp foot 25`)                 |
| **Show *****all***** notes**                | `stamp foot all`                                      |
| **Show timestamp of note #X**               | `stamp notetime X` (1-based index)                    |
| **Show note whose timestamp starts with Y** | `stamp timenote Y` (e.g. `stamp timenote 2025-07-30`) |

A success message after each note looks like:

```
stamp success: page daily_log timestamp 2025-07-30 15:42:01 note fixed bug in…
```

---

## 4 Installation

### 4.1 Using pip

```
bash
pip install git+https://github.com/<user>/timestampr.git   # latest from GitHub
```

### 4.2 From source

```
bash
git clone https://github.com/<user>/timestampr.git
cd timestampr
pip install .
```

---

## 5 Dependencies

Runtime: **Python ≥ 3.8** and the **standard library** – no external packages required.\
Packaging-time: *setuptools* (installed automatically by `pip`).

---

## 6 File locations

| Item            | Location                             |
| --------------- | ------------------------------------ |
| User config     | `~/.timestampr/config.json`          |
| Notebook folder | path provided in `stamp newnotebook` |
| Page files      | `<notebook>/<page>.csv`              |

---

## 7 Back-ups & syncing

Because everything is plain text, simply back-up or sync your notebook folder (e.g. with Git, Dropbox, Syncthing, etc.).

---

## 8 Uninstall

```
bash
pip uninstall timestampr        # removes the CLI tool
rm -rf ~/.timestampr            # removes stored config (optional)
```

Enjoy quick, timestamped note-taking!

# AGENTS.md

# AGENTS GUIDE – timestampr

This document explains repository structure, coding conventions, and the workflow expected of any automated or human contributor ("agent").

---

## 1 Repository layout

| Path                | Purpose                                              |
| ------------------- | ---------------------------------------------------- |
| `timestampr/cli.py` | **Only** executable code – CLI entry-point & helpers |
| `pyproject.toml`    | Build recipe & CLI mapping (`stamp`)                 |
| `README.md`         | User documentation                                   |
| `AGENTS.md`         | *This* file – agent guidance & change log            |

---

## 2 Coding guidelines

1. **Python ≥ 3.8**; stick to the standard library – no external runtime deps.
2. Every new function must have a docstring.
3. Run `python -m pip install -e .[dev]` then `pytest` (future test suite).
4. Preserve backward compatibility of the CLI interface listed in `README.md`.
5. User config lives at `~/.timestampr/config.json`; do **NOT** move or rename this without a major version bump.

---

## 3 Branch / PR conventions

- `main` – stable, released code
- `dev/*` – feature branches
- Require at least one approving review (or CI green tick for bot commits)

---

## 4 CI expectations

Future CI will run:

```
bash
python -m pip install -e .[dev]
python -m pytest
python -m pip check
ruff check timestampr       # lint
```

---

## 5 Network domains in build-time

| Purpose             | Domain                               |
| ------------------- | ------------------------------------ |
| Clone / push        | `github.com`                         |
| Fetch PyPI packages | `pypi.org`, `files.pythonhosted.org` |

No runtime network access is necessary.

---

## 6 Changelog logging policy

*Every* agent (human or automated) **must** append a brief entry to the end of this file **in the format below** describing:

- what changed
- why it changed
- any issues encountered

### Example entry

```
## 2025-07-30  @ci-bot

* Added rudimentary pytest suite (tests/test_cli.py)  
  – verifies `stamp -` appends a row  
* No issues
```

---

## 7 Open TODOs

- Add unit tests (`pytest`)
- Optional enhancement: coloured output (`rich`; would add optional dep)

---

## 8 Change log

*(append below – newest at bottom)*

