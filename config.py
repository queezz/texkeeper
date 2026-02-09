"""Configuration loader for project-local texkeeper.toml."""
import tomllib
from pathlib import Path

from keeper.paths import ROOT

CONFIG_FILE = ROOT / "texkeeper.toml"


def load_config() -> dict:
    """
    Load texkeeper.toml from project root.

    Returns empty dict if file doesn't exist or is invalid.
    """
    if not CONFIG_FILE.exists():
        return {}

    try:
        with open(CONFIG_FILE, "rb") as f:
            return tomllib.load(f)
    except Exception:
        # Silently fail and return empty dict to fall back to defaults
        return {}
