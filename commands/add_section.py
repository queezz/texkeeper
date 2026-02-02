import sys
from pathlib import Path

from keeper.latex.chapters import CHAPTER_TEMPLATE
from keeper.latex.master import (
    build_master_content,
    extract_section_order,
    load_master_sections,
)
from keeper.models import MasterSection
from keeper.paths import CHAPTERS_DIR, MASTER, ROOT


def run(section_slug: str, title: str):
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
