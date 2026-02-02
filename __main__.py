from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path

import argparse
import re
import shutil
import sys

ROOT = Path.cwd()

CHAPTERS_DIR = ROOT / "chapters"
FIRST_CHAPTER = CHAPTERS_DIR / "10-chapter.tex"
MASTER = ROOT / "master.tex"
PREAMBLE = ROOT / "preamble.tex"
PDF_ARCHIVE = ROOT / "PDFs"

# -------------------------------------------------
# MARK: Embedded assets
# -------------------------------------------------
def load_preamble_text() -> str:
    try:
        return (
            files("keeper.assets")
            .joinpath("preamble.tex")
            .read_text(encoding="utf-8")
        )
    except ModuleNotFoundError:
        asset_path = Path(__file__).resolve().parent / "assets" / "preamble.tex"
        return asset_path.read_text(encoding="utf-8")

PREAMBLE_TEXT = load_preamble_text().lstrip()

MASTER_TEXT = r"""
\documentclass[a5paper,10pt]{extarticle}
\input{preamble.tex}

\begin{document}

\setdocumenttitle{ }

\subfile{chapters/10-chapter.tex}

\end{document}
""".lstrip()


LATEX_JUNK = {
    ".aux",
    ".log",
    ".out",
    ".synctex.gz",
    ".synctex.gz.sum.synctex",
    ".toc",
    ".nav",
    ".snm",
    ".fdb_latexmk",
    ".fls",
    ".bbl",
    ".blg",
}

BEGIN_DOCUMENT = r"\begin{document}"
END_DOCUMENT = r"\end{document}"
SETHEADER_RE = re.compile(r"\\setheader\{(.+)\}")
SUBFILE_RE = re.compile(r"\\subfile\{(.+?)\}")


@dataclass
class MasterSection:
    order: int
    title: str
    subfile: str


CHAPTER_TEMPLATE = (
    "\\documentclass[subfiles]{extarticle}\n\n"
    "\\begin{document}\n\n"
    "\\section{%TITLE%}\n\n"
    "% TODO: Add content for %TITLE%.\n\n"
    "\\end{document}\n"
)


def extract_section_order(subfile: str) -> int:
    name = Path(subfile).name
    match = re.match(r"(\d+)", name)
    if not match:
        raise ValueError(f"Section file {name!r} must begin with a numeric prefix.")
    return int(match.group(1))


def _parse_master_sections(body: str) -> list[MasterSection]:
    lines = body.splitlines()
    sections: list[MasterSection] = []
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if not stripped:
            i += 1
            continue
        header_match = SETHEADER_RE.match(stripped)
        if header_match:
            title = header_match.group(1)
            i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1
            if i >= len(lines):
                break
            subfile_line = lines[i].strip()
            subfile_match = SUBFILE_RE.match(subfile_line)
            if not subfile_match:
                raise ValueError("Malformed \\subfile entry near \\setheader.")
            subfile = subfile_match.group(1)
            sections.append(
                MasterSection(
                    order=extract_section_order(subfile), title=title, subfile=subfile
                )
            )
            i += 1
            while i < len(lines) and lines[i].strip() != "\\newpage":
                i += 1
            if i < len(lines) and lines[i].strip() == "\\newpage":
                i += 1
            continue
        i += 1
    return sections


def load_master_sections() -> tuple[str, list[MasterSection], str]:
    text = MASTER.read_text(encoding="utf-8")
    begin_idx = text.index(BEGIN_DOCUMENT)
    end_idx = text.index(END_DOCUMENT, begin_idx)
    before = text[:begin_idx]
    body = text[begin_idx + len(BEGIN_DOCUMENT) : end_idx]
    after = text[end_idx + len(END_DOCUMENT) :]
    sections = _parse_master_sections(body)
    return before, sections, after


def build_master_content(before: str, sections: list[MasterSection], after: str) -> str:
    chunks = []
    for section in sections:
        chunks.append(
            "\n".join(
                (
                    f"\\setheader{{{section.title}}}",
                    f"\\subfile{{{section.subfile}}}",
                    "\\newpage",
                )
            )
        )
    if chunks:
        body = "\n\n" + "\n\n".join(chunks) + "\n\n"
    else:
        body = "\n\n"
    return f"{before}{BEGIN_DOCUMENT}{body}{END_DOCUMENT}{after}"


# -------------------------------------------------
# MARK:Helpers
# -------------------------------------------------


def write_if_missing(path: Path, content: str):
    if not path.exists():
        path.write_text(content, encoding="utf-8")


# -------------------------------------------------
# MARK: Commands
# -------------------------------------------------


def cmd_init():
    """
    Initialize a new thinking workspace.

    Creates:
      - chapters/
      - preamble.tex
      - master.tex
      - chapters/10-chapter.tex

    Existing files are never overwritten.
    """
    CHAPTERS_DIR.mkdir(parents=True, exist_ok=True)

    write_if_missing(PREAMBLE, PREAMBLE_TEXT)
    write_if_missing(MASTER, MASTER_TEXT)
    write_if_missing(FIRST_CHAPTER, "")

    print("Workspace initialized.")


def cmd_clean():
    """
    Remove LaTeX temporary / build files from the project tree.
    """
    deleted = []

    for p in ROOT.rglob("*"):
        if p.is_file() and (
            p.suffix in LATEX_JUNK or any(str(p).endswith(x) for x in LATEX_JUNK)
        ):
            try:
                p.unlink()
                deleted.append(p)
            except Exception as e:
                print(f"Could not delete {p}: {e}")

    print(f"Deleted {len(deleted)} LaTeX temp files.")


def cmd_add_section(section_slug: str, title: str):
    """
    Register a numbered section and scaffold the chapter stub.

    The slug (e.g., 20-permeation-gas-driven-multilayer-membrane) becomes the
    ./chapters/ slug.tex file and determines ordering by its leading digits
    (10, 20, etc.). The title is reused for both \\setheader and the default
    \\section heading inside the new chapter.
    """
    CHAPTERS_DIR.mkdir(parents=True, exist_ok=True)

    slug_path = Path(section_slug)
    chapter_name = slug_path.name or section_slug
    if not chapter_name.endswith(".tex"):
        chapter_name = f"{chapter_name}.tex"

    try:
        order = extract_section_order(chapter_name)
    except ValueError as exc:
        print(exc)
        sys.exit(1)

    before, sections, after = load_master_sections()
    rel_path = f"./chapters/{chapter_name}"
    existing = next((s for s in sections if Path(s.subfile).name == chapter_name), None)
    if existing:
        existing.title = title
        existing.order = order
        existing.subfile = rel_path
        print(f"Updated {chapter_name} entry in {MASTER.name}.")
    else:
        sections.append(MasterSection(order=order, title=title, subfile=rel_path))
        print(f"Added {chapter_name} entry to {MASTER.name}.")

    sections.sort(key=lambda s: s.order)

    chapter_path = CHAPTERS_DIR / chapter_name
    if chapter_path.exists():
        print(
            f"Chapter file {chapter_path.relative_to(ROOT)} already exists; skipping template."
        )
    else:
        chapter_path.write_text(
            CHAPTER_TEMPLATE.replace("%TITLE%", title), encoding="utf-8"
        )
        print(f"Created chapter template at {chapter_path.relative_to(ROOT)}.")

    MASTER.write_text(build_master_content(before, sections, after), encoding="utf-8")


def cmd_pdf(overwrite=False):
    """
    Copy generated PDFs into ./PDFs for archiving.

    Existing archives are kept intact unless the --overwrite flag is used.
    """
    PDF_ARCHIVE.mkdir(parents=True, exist_ok=True)

    copied = []

    search_dirs = [ROOT, CHAPTERS_DIR]

    for base in search_dirs:
        if not base.exists():
            continue

        for p in base.rglob("*.pdf"):

            # Skip already archived PDFs
            if PDF_ARCHIVE in p.parents:
                continue

            target = PDF_ARCHIVE / p.name

            if target.exists() and not overwrite:
                continue

            shutil.copy(p, target)
            copied.append(p.relative_to(ROOT))

    if not copied:
        print("No PDFs copied.")
    else:
        for p in copied:
            print(f"Copied: {p}")


# -------------------------------------------------
# MARK: CLI
# -------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        prog="keeper.py",
        description=(
            "keeper.py — a small caretaker for a LaTeX thinking workspace\n\n"
            "Typical workflow:\n"
            "  python keeper.py init\n"
            "  latexmk master.tex\n"
            "  python keeper.py clean\n"
            "  python keeper.py pdf\n\n"
            "PDF options:\n"
            "  python keeper.py pdf --overwrite  overwrite existing PDFs in ./PDFs\n"
            "\n"
            "Section helpers:\n"
            '  python keeper.py add-section 31-work-in-progress "Work in Progress"'
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser(
        "init",
        help="initialize project structure (safe to re-run)",
        description=cmd_init.__doc__,
    )

    sub.add_parser(
        "clean",
        help="remove LaTeX temporary files",
        description=cmd_clean.__doc__,
    )

    pdf = sub.add_parser(
        "pdf",
        help="copy PDFs to ./PDFs",
        description=cmd_pdf.__doc__,
    )
    pdf.add_argument(
        "--overwrite",
        action="store_true",
        help="overwrite existing PDFs in ./PDFs",
    )
    add_section = sub.add_parser(
        "add-section",
        help="register a new chapter section and stub file",
        description=cmd_add_section.__doc__,
    )
    add_section.add_argument(
        "slug",
        help="slug used for the chapter filename (e.g. 20-permeation-gas-driven-multilayer-membrane)",
    )
    add_section.add_argument(
        "title",
        help="header text for \\setheader and the default \\section within the chapter",
    )

    sub.add_parser(
        "help",
        help="show this help message",
    )

    args = parser.parse_args()

    if args.cmd == "init":
        cmd_init()
    elif args.cmd == "clean":
        cmd_clean()
    elif args.cmd == "pdf":
        cmd_pdf(args.overwrite)
    elif args.cmd == "add-section":
        cmd_add_section(args.slug, args.title)
    else:
        parser.print_help()



# -------------------------------------------------
# MARK: Main
# -------------------------------------------------

if __name__ == "__main__":
    main()
