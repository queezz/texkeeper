import shutil
from pathlib import Path

from keeper.config import load_config
from keeper.paths import CHAPTERS_DIR, PDF_ARCHIVE, ROOT


def run(overwrite=False):
    """
    Copy generated PDFs to configured destinations.

    Existing archives are kept intact unless the --overwrite flag is used.
    """
    cfg = load_config()

    # Use config if available, otherwise fall back to defaults
    if "pdf" in cfg:
        pdf_cfg = cfg["pdf"]
        copy_to = pdf_cfg.get("copy_to", [])
        
        if not copy_to:
            print("No copy destinations configured.")
            return

        copied = []
        pdfs_to_copy = []

        # Collect master PDF if configured
        if pdf_cfg.get("copy_master", False):
            master_source = pdf_cfg.get("master_source", "build/master.pdf")
            master_path = Path(master_source)
            if not master_path.is_absolute():
                master_path = ROOT / master_path
            
            if master_path.exists():
                pdfs_to_copy.append(master_path)
            else:
                print(f"Master PDF not found: {master_path} (skipping)")

        # Collect PDFs from folders if configured
        if pdf_cfg.get("copy_from_folders", False):
            folder_paths = pdf_cfg.get("folder_paths", ["chapters"])
            recursive = pdf_cfg.get("recursive", True)
            
            for folder_str in folder_paths:
                folder_path = Path(folder_str)
                if not folder_path.is_absolute():
                    folder_path = ROOT / folder_path
                
                if not folder_path.exists():
                    print(f"Folder not found: {folder_path} (skipping)")
                    continue
                
                if folder_path.is_file():
                    # If it's a file and it's a PDF, add it
                    if folder_path.suffix == ".pdf":
                        pdfs_to_copy.append(folder_path)
                elif folder_path.is_dir():
                    # Search for PDFs in the folder
                    if recursive:
                        for pdf_file in folder_path.rglob("*.pdf"):
                            pdfs_to_copy.append(pdf_file)
                    else:
                        for pdf_file in folder_path.glob("*.pdf"):
                            pdfs_to_copy.append(pdf_file)

        # Copy all collected PDFs to all destinations
        for pdf_path in pdfs_to_copy:
            for dest in copy_to:
                dest_path = Path(dest)
                if not dest_path.is_absolute():
                    dest_path = ROOT / dest_path

                dest_path.mkdir(parents=True, exist_ok=True)
                target = dest_path / pdf_path.name

                if target.exists() and not overwrite:
                    continue

                shutil.copy(pdf_path, target)
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
