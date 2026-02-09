"""Generate default texkeeper.toml configuration file."""
from pathlib import Path

from keeper.config import CONFIG_FILE

DEFAULT_CONFIG = """[watch]
paths = [
  ".",
]

[pdf]
# Copy master PDF if it exists
copy_master = false
master_source = "master.pdf"

# Copy PDFs from folders
copy_from_folders = true
folder_paths = [
  "."
]
recursive = false

# Copy destinations
copy_to = [
  "./PDFs",
  # "/absolute/path/if/user/wants"
]
"""


def run():
    """
    Generate a default texkeeper.toml configuration file in the project root.

    Safe to re-run — existing config files are never overwritten.
    """
    if CONFIG_FILE.exists():
        print(f"{CONFIG_FILE.name} already exists. Not overwriting.")
        return

    CONFIG_FILE.write_text(DEFAULT_CONFIG, encoding="utf-8")
    print(f"Created {CONFIG_FILE.name} in project root.")
    print("Edit it to customize watch paths and PDF copy destinations.")
