# README: timestampr(CLI)

A bare-bones note-taker that timestamps everything.

---

## 0 - Imagine

Your notebook was laying open while you worked. You were multi-tasking. You were sporadically jotting down notes. You were working late to meet a deadline. Repeat ad nauseam. Now skip ahead a year or more. You need to write a grad thesis based on those notes.

If you were using pen and paper:
- your notes are probably a mess;
- you will waste a month of Sundays trying to decipher them;
- you might need to defer your graduation.

If you were using `timestampr(CLI)`:
- your notes were timestamped and filed (by date or topic);
- your notes are now searchable, sortable, and exportable;
- you might have time to go camping this weekend.

---

## 1 - What it does

`timestampr(CLI)` lets you jot ultra-quick notes from any terminal.\
Each notebook is just a folder on your laptop;\
Each page is a `.csv` file inside that folder;\
Each line is now:

```
YYYY-MM-DD,HH:MM:SS,Your note text…
```

Since it is plain text, you can easily **grep**, **sync to the cloud**, or **open in Excel**.

---

## 2 - Quick start

```
bash
# 1. pick or create a folder for your notebook
stamp newnotebook              # will ask for the path

# 2. pick or create a page
stamp newpage                  # name it or press <Enter> for an auto-dated page

# 3. write notes
stamp - fixed issue #42
stamp - inoculated flasks 7-9
```

---

## 3 - Commands available

| Command & arguments                                   | Action                                  |
| ----------------------------------------------------- | --------------------------------------- |
| `stamp - <note text>`                                 | New note                                |
| `stamp newpage`                                       | New page (prompt)                       |
| `stamp newnotebook`                                   | New notebook (prompt)                   |
| `stamp active`                                        | Show active notebook & page             |
| `stamp page`                                          | Change page                             |
| `stamp notebook`                                      | Change notebook                         |
| `stamp foot`                                          | Show last 10 notes                      |
| `stamp foot N` (e.g. `stamp foot 25`)                 | Show last N notes                       |
| `stamp foot all`                                      | Show all notes                          |
| `stamp notetime X` (1-based index)                    | Show timestamp of note #X               |
| `stamp timenote Y` (e.g. `stamp timenote 08:30`)      | Show notes at time Y or range |
| `stamp search text`                                   | Find notes containing `text` |

For peace of mind, a message like this appears every time a note is added successfully:

```
stamp success: daily_log 2025-07-30 15:42:01 fixed bug in…
```

---

## 4 - Installation

### 4.1 Using pip

```
bash
pip install git+https://github.com/Donnie-McFarlane/timestampr.git
```

### 4.2 From source

```
bash
git clone https://github.com/Donnie-McFarlane/timestampr.git
cd timestampr
pip install .
```

---

## 5 - Dependencies

Runtime: **Python ≥ 3.8** and the **standard library** – no external packages required.\
Packaging-time: *setuptools* (installed automatically by `pip`).

---

## 6 - File locations

| Item            | Location                             |
| --------------- | ------------------------------------ |
| User config     | `~/.timestampr/config.json`          |
| Notebook folder | path provided by `stamp newnotebook` |
| Page files      | `<notebook>/<page>.csv`              |

---

## 7 - Back-ups & syncing

Because everything is plain text, simply back-up or sync your notebook folder (e.g. with Git, Dropbox, OneDrive, etc.).

---

## 8 - Uninstall

```
bash
pip uninstall timestampr        # removes the CLI tool
rm -rf ~/.timestampr            # removes stored config (optional)
```

---

Thanks for reading! I hope my little side-quest here helps you to stay organized and save a bit of time for yourself.
