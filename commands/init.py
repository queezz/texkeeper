from importlib.resources import files
from pathlib import Path

from keeper.paths import CHAPTERS_DIR, MASTER, PREAMBLE


def _read_asset_text(asset_name: str) -> str:
    try:
        return files("keeper.assets").joinpath(asset_name).read_text(encoding="utf-8")
    except ModuleNotFoundError:
        asset_path = Path(__file__).resolve().parents[1] / "assets" / asset_name
        return asset_path.read_text(encoding="utf-8")


def _write_if_missing(path: Path, content: str):
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def run():
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

    preamble_text = _read_asset_text("preamble.tex")
    master_text = _read_asset_text("master.tex")

    _write_if_missing(PREAMBLE, preamble_text)
    _write_if_missing(MASTER, master_text)
    print("Workspace initialized.")
