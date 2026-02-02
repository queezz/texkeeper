import shutil

from keeper.paths import CHAPTERS_DIR, PDF_ARCHIVE, ROOT


def run(overwrite=False):
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
