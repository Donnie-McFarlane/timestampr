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
3. **Before committing**, run `python -m pip install -e .[dev]` then `pytest`.
   Once tests pass with no errors, update all documentation that references the
   changed functionality.
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

## 2025-07-30  @assistant

* Split README_and_AGENTS.md into README.md and AGENTS.md; removed old README
* Added initial test suite and updated docs
* No issues

## 2025-07-30  @Donnie

* Reworked README intro and command table; other minor wording fixes
* No issues

