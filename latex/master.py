import re
from pathlib import Path

from keeper.models import MasterSection
from keeper.paths import MASTER
from keeper.regexes import BEGIN_DOCUMENT, END_DOCUMENT, SETHEADER_RE, SUBFILE_RE


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
