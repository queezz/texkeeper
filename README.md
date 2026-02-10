# keeper

**keeper** is a tiny command-line caretaker for a LaTeX “thinking workspace”.

It creates a minimal project scaffold, keeps the directory clean from LaTeX junk,
helps manage chapter files, and collects generated PDFs in one place — without
getting in your way.

This is not a build system.  
It’s a broom, a clipboard, and a notebook label.

---

## Contents

- [Philosophy](#philosophy)
- [Installation](#installation)
- [Project structure](#project-structure)
- [Usage](#usage)
- [Typical workflow](#typical-workflow)
- [Commands](#commands)
- [Requirements](#requirements)
- [Non-goals](#non-goals)
- [Why this exists](#why-this-exists)
- [LaTeX preamble helpers](#latex-preamble-boxes-and-commands)

---

## Philosophy

- One file, one purpose
- Safe to re-run (no silent overwrites)
- Optional project-local config (not required)
- You still run `latexmk` yourself
- Optimized for long-lived, messy thinking projects

---

## Installation

Clone `keeper` **into your project root** as `.keeper`:

```bash
git clone https://github.com/queezz/texkeeper.git .keeper
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
├─ texkeeper.toml  (optional, for project-local config)
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

### `init-config`

Generate a default `texkeeper.toml` configuration file in the project root.

This file allows you to configure:
* Which paths to watch for file changes
* PDF source location and copy destinations

Safe to re-run — existing config files are never overwritten.

```bash
python .keeper init-config
```

This creates `texkeeper.toml` with example configuration. Edit it to customize watch paths and PDF behavior.

---

### `watch`

Watch configured paths for file changes.

Uses paths from `texkeeper.toml` `[watch]` section, or defaults to watching the current directory (`.`) if no config exists.

**Example usage:**

```bash
# Start watching (uses config if texkeeper.toml exists, otherwise watches ".")
python .keeper watch
```

The watch command will:
* Display which paths are being watched
* Monitor files for changes
* Print notifications when files are modified
* Run until interrupted with Ctrl+C

**Example output:**

```
Watching 3 path(s):
  .
  sections
  figures

Monitoring for changes (Ctrl+C to stop)...
Changed: sections/01-intro.tex
Changed: figures/diagram.pdf
```

**Configuration example** (`texkeeper.toml`):

```toml
[watch]
paths = [
  ".",
  "sections",
  "figures"
]
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

Copy generated PDFs to configured destinations.

**Without config** (default behavior):
* Searches project root and `chapters/` for PDFs recursively
* Copies them to `./PDFs`
* Skips already archived PDFs by default

```bash
python .keeper pdf
```

**With config** (`texkeeper.toml`):
* Optionally copies master PDF if it exists
* Optionally copies PDFs from configured folders
* Copies to all configured `copy_to` destinations
* Creates destination folders if needed

```bash
python .keeper pdf
```

Overwrite existing PDFs:

```bash
python .keeper pdf --overwrite
```

**Configuration example** (`texkeeper.toml`):

```toml
[pdf]
# Copy master PDF if it exists
copy_master = true
master_source = "build/master.pdf"

# Copy PDFs from folders
copy_from_folders = true
folder_paths = [
  "chapters",
  "sections"
]
recursive = true

# Copy destinations
copy_to = [
  "../exports",
  # "/absolute/path/if/user/wants"
]
```

**Configuration options:**
* `copy_master` (boolean): Whether to copy the master PDF
* `master_source` (string): Path to master PDF (relative to project root or absolute)
* `copy_from_folders` (boolean): Whether to copy PDFs from folders
* `folder_paths` (list): Folders to search for PDFs
* `recursive` (boolean): Whether to search folders recursively
* `copy_to` (list): Destination folders for copied PDFs

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

* Python 3.11+ (for `tomllib` support in config)
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

---

## LaTeX preamble: boxes and commands

The default `preamble.tex` scaffolded by `keeper` ships with a few quality‑of‑life helpers:

- **Box environments**
  - **`graybox{<title>}`**: Framed block with a left rule and a title bar, good for highlighted notes or definitions.
  - **`simplegraybox`**: Simple, untitled gray box for short remarks or inline derivations.
  - **`bluebox{<title>}`**: Blue framed box with a tinted title ribbon, intended for final answers / key results.

- **Header helper**
  - **`\setheader{<text>}`**: Sets the left side of the running header (right side always shows the page number).

- **Math convenience**
  - **`\conjugatet{z}`**: Alias for `\overline{z}` (complex conjugate), exposed so you can use a consistent notation and swap implementations later if needed.

