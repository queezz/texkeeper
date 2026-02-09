import shutil
from pathlib import Path

from keeper.config import load_config
from keeper.paths import CHAPTERS_DIR, PDF_ARCHIVE, ROOT


def run(overwrite=False):
    """
    Copy generated PDFs into ./PDFs for archiving.

    Existing archives are kept intact unless the --overwrite flag is used.
    """
    cfg = load_config()

    # Use config if available, otherwise fall back to defaults
    if "pdf" in cfg and "source" in cfg["pdf"]:
        # New config-based behavior: copy from specific source to configured destinations
        source_path = Path(cfg["pdf"]["source"])
        if not source_path.is_absolute():
            source_path = ROOT / source_path

        if not source_path.exists():
            print(f"PDF source not found: {source_path}")
            return

        copy_to = cfg["pdf"].get("copy_to", [])
        if not copy_to:
            print("No copy destinations configured.")
            return

        copied = []
        for dest in copy_to:
            dest_path = Path(dest)
            if not dest_path.is_absolute():
                dest_path = ROOT / dest_path

            dest_path.mkdir(parents=True, exist_ok=True)
            target = dest_path / source_path.name

            if target.exists() and not overwrite:
                continue

            shutil.copy(source_path, target)
            try:
                copied.append(target.relative_to(ROOT))
            except ValueError:
                copied.append(target)

        if not copied:
            print("No PDFs copied.")
        else:
            for p in copied:
                print(f"Copied: {p}")
    else:
        # Default behavior: search and archive to ./PDFs
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
