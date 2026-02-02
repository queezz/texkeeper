from keeper.latex.junk import LATEX_JUNK
from keeper.paths import ROOT


def run():
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
