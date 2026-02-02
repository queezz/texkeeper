# keeper

**keeper** is a tiny command-line caretaker for a LaTeX “thinking workspace”.

It creates a minimal project scaffold, keeps the directory clean from LaTeX junk,
helps manage chapter files, and collects generated PDFs in one place — without
getting in your way.

This is not a build system.  
It’s a broom, a clipboard, and a notebook label.

---

## Philosophy

- One file, one purpose
- Safe to re-run (no silent overwrites)
- No magic state, no config files
- You still run `latexmk` yourself
- Optimized for long-lived, messy thinking projects

---

## Installation

Clone `keeper` **into your project root** as `.keeper`:

```bash
git clone git@github.com:queezz/texkeeper.git .keeper
```

No installation, no virtual environment, no PATH setup.

---

## Project structure

After initialization:

```
.
├─ master.tex
├─ preamble.tex
├─ chapters/
│  └─ 10-chapter.tex
├─ PDFs/
└─ .keeper/
   ├─ __main__.py
   ├─ __init__.py
   └─ ...
```

`.keeper/` is an external helper tool and is typically added to `.gitignore`.

---

## Usage

Run all commands **from the project root**:

```bash
python .keeper <command>
```

---

## Typical workflow

```bash
python .keeper init
latexmk master.tex
python .keeper clean
python .keeper pdf
python .keeper add-section 20-permeation-model "Permeation Model"
```

---

## Commands

### `init`

Initialize a new thinking workspace.

Creates (if missing):

* `chapters/`
* `preamble.tex`
* `master.tex`
* `chapters/10-chapter.tex`

Safe to run multiple times — existing files are never overwritten.

```bash
python .keeper init
```

---

### `clean`

Remove LaTeX temporary/build files recursively.

Deletes common junk such as:

`.aux`, `.log`, `.fls`, `.fdb_latexmk`, `.synctex.gz`, etc.

```bash
python .keeper clean
```

---

### `pdf`

Copy generated PDFs into `./PDFs`.

* Searches project root and `chapters/`
* Skips already archived PDFs by default

```bash
python .keeper pdf
```

Overwrite existing archives:

```bash
python .keeper pdf --overwrite
```

---

### `add-section`

Register a numbered chapter and scaffold its file.

The numeric prefix determines ordering in `master.tex`.

```bash
python .keeper add-section 20-permeation-model "Permeation Model"
```

Creates:

```
chapters/20-permeation-model.tex
```

And updates `master.tex` accordingly.

Re-running with the same slug updates the title but keeps content intact.

---

### `help`

Show CLI help.

```bash
python .keeper help
```

---

## Requirements

* Python 3.10+
* No external dependencies
* LaTeX toolchain (`latexmk`, etc.) is assumed but not managed

---

## Non-goals

keeper intentionally does **not**:

* run LaTeX for you
* manage bibliographies
* track build state
* enforce document structure
* introduce configuration files

If you want those things, use a heavier tool.

---

## Why this exists

I am lazy about tooling, not about writing.

Every IDE wants configuration. Every configuration wants maintenance.
keeper avoids all of that by doing the minimum necessary work in plain sight.

No editor lock-in. No project metadata. No hidden state.
Just files, Python, and LaTeX.

This is not a recommendation.
It’s a convenience.

