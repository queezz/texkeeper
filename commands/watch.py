"""Watch files/folders for changes."""
import time
from pathlib import Path

from keeper.config import load_config
from keeper.paths import ROOT


def run():
    """
    Watch configured paths for file changes.

    Uses paths from texkeeper.toml [watch] section, or defaults to "." if not configured.
    """
    cfg = load_config()

    # Get watch paths from config, default to ["."] if not set
    if "watch" in cfg and "paths" in cfg["watch"]:
        watch_paths = cfg["watch"]["paths"]
    else:
        watch_paths = ["."]

    # Resolve paths relative to project root
    resolved_paths = []
    for path_str in watch_paths:
        path = Path(path_str)
        if not path.is_absolute():
            path = ROOT / path
        if path.exists():
            resolved_paths.append(path)
        else:
            print(f"Warning: Watch path does not exist: {path}")

    if not resolved_paths:
        print("No valid watch paths configured.")
        return

    print(f"Watching {len(resolved_paths)} path(s):")
    for p in resolved_paths:
        try:
            print(f"  {p.relative_to(ROOT)}")
        except ValueError:
            print(f"  {p}")

    # Simple file monitoring loop
    # This is a minimal implementation - VS Code handles the actual compilation
    last_modified = {}
    for path in resolved_paths:
        if path.is_file():
            last_modified[path] = path.stat().st_mtime
        elif path.is_dir():
            for file_path in path.rglob("*"):
                if file_path.is_file():
                    last_modified[file_path] = file_path.stat().st_mtime

    print("\nMonitoring for changes (Ctrl+C to stop)...")

    try:
        while True:
            time.sleep(1)
            changed = []
            for file_path, last_mtime in list(last_modified.items()):
                if not file_path.exists():
                    continue
                current_mtime = file_path.stat().st_mtime
                if current_mtime > last_mtime:
                    changed.append(file_path)
                    last_modified[file_path] = current_mtime

            # Check for new files
            for path in resolved_paths:
                if path.is_file() and path not in last_modified:
                    last_modified[path] = path.stat().st_mtime
                    changed.append(path)
                elif path.is_dir():
                    for file_path in path.rglob("*"):
                        if file_path.is_file() and file_path not in last_modified:
                            last_modified[file_path] = file_path.stat().st_mtime
                            changed.append(file_path)

            if changed:
                for file_path in changed:
                    try:
                        rel_path = file_path.relative_to(ROOT)
                    except ValueError:
                        rel_path = file_path
                    print(f"Changed: {rel_path}")
    except KeyboardInterrupt:
        print("\nStopped watching.")
