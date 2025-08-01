# timestampr(CLI)

A bare-bones note-taker. Dead simple to use. Helps keep you on track.

---

>## 0 - Prologue
>
> #### *Imagine:*
> Your notebook was laying open while you worked. You were multi-tasking. You were sporadically jotting down notes. You were working late to meet a deadline. Repeat ad nauseam. Now skip ahead a year or more. You need to write a grad thesis based on those notes.
>
>If you were using pen and paper:
>- your notes are probably a mess;
>- you will waste a month of Sundays trying to decipher them;
>- you might need to defer your graduation.
>
>If you were using `timestampr(CLI)`:
>- your notes were timestamped and filed (by date or topic);
>- your notes are now searchable, sortable, and exportable;
>- you might have time to go camping this weekend.

---

## 1 - What it does

`timestampr(CLI)` lets you jot ultra-quick notes from any terminal.\
Each notebook is just a folder on your laptop;\
Each page is a `.csv` file inside that folder;\
Each line is:

```
YYYY-MM-DD,HH:MM:SS,Your note text…
```

Since it is plain text, you can easily **grep**, **sync to the cloud**, or **open in Excel**.

---

## 2 - Quick start

```
bash
# 1. pick or create a folder for your notebook
stamp notebook              # will ask for the path

# 2. pick or create a page
stamp page                  # name it or press <Enter> for an auto-dated page

# 3. write notes
stamp - fixed issue #42
stamp - inoculated flasks 7-9
```

---

## 3 - Commands available

| Command & arguments                                   | Action                                  |
| ----------------------------------------------------- | --------------------------------------- |
| `stamp - <note text>`                                 | New note                                |
| `stamp active`                                        | Display active notebook & page          |
| `stamp page`                                          | Change page                             |
| `stamp notebook`                                      | Change notebook                         |
| `stamp show ...` (`head` / `foot` / `all`)            | Show notes (first 10 or last 10 or `all`) |
| `stamp show N` (e.g. `stamp show 27`)                 | Show notes at index `N` (or range `N to M`) |
| `stamp timenote Y` (e.g. `stamp timenote 08:30`)      | Show notes at time `Y` (or range `Y to Z`)  |
| `stamp search keyword`                                | Search notes containing `keyword`       |

For peace of mind, a message like this appears every time a note is added successfully:

```
stamp success: wetlab_log 2025-07-30 15:42:01 inoculated all flasks for overnight culture…
```

---

## 4 - Installation

### 4.1 Using pip

```
bash
pip install git+https://github.com/Donnie-McFarlane/timestampr.git
```
On Windows you may need to use `py -m pip` instead of `pip`.

### 4.2 From source

```
bash
git clone https://github.com/Donnie-McFarlane/timestampr.git
cd timestampr
pip install .
```
Again, Windows users can run `py -m pip install .` if needed.

---

## 5 - Dependencies

Runtime: **Python ≥ 3.8** and the **standard library** – no external packages required.\
Packaging-time: *setuptools* (installed automatically by `pip`). The CLI works
on Linux, macOS **and Windows** so long as a compatible Python interpreter is
available.

---

## 6 - File locations

| Item            | Location                             |
| --------------- | ------------------------------------ |
| User config     | `~/.timestampr/config.json` (on Windows: `C:\\Users\\<you>\\.timestampr\\config.json`) |
| Notebook folder | path provided by `stamp notebook` |
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
