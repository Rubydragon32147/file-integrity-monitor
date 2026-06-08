import json
import os
from datetime import datetime
from hasher import hash_directory

def create_baseline(config: dict) -> dict:
    baseline = {}
    for path in config["watch_paths"]:
        if os.path.exists(path):
            hashes = hash_directory(path, config["ignored_extensions"])
            baseline.update(hashes)

    snapshot = {
        "created_at": datetime.now().isoformat(),
        "files": baseline
    }
    with open(config["baseline_file"], "w") as f:
        json.dump(snapshot, f, indent=2)

    save_restore_copies(baseline)   # ← add this line
    return snapshot

def load_baseline(config: dict) -> dict | None:
    """Load existing baseline. Returns None if file doesn't exist."""
    path = config["baseline_file"]
    if not os.path.exists(path):
        return None
    with open(path) as f:
        data = json.load(f)
    return data.get("files", {})

def compare_to_baseline(current: dict, baseline: dict) -> list:
    """
    Compare current file hashes to baseline.
    Returns a list of change dicts: {type, path, old_hash, new_hash}
    """
    changes = []
    current_paths = set(current.keys())
    baseline_paths = set(baseline.keys())

    # Modified or new files
    for path in current_paths:
        if path not in baseline_paths:
            changes.append({"type": "NEW", "path": path, "old_hash": None, "new_hash": current[path]})
        elif current[path] != baseline[path]:
            changes.append({"type": "MODIFIED", "path": path, "old_hash": baseline[path], "new_hash": current[path]})

    # Deleted files
    for path in baseline_paths:
        if path not in current_paths:
            changes.append({"type": "DELETED", "path": path, "old_hash": baseline[path], "new_hash": None})

    return changes  

import shutil

RESTORE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".fims_restore")

def save_restore_copies(baseline: dict):
    """Save a copy of every baselined file for future restore."""
    if os.path.exists(RESTORE_DIR):
        shutil.rmtree(RESTORE_DIR)
    os.makedirs(RESTORE_DIR)

    for filepath in baseline.keys():
        if os.path.exists(filepath):
            # Flatten path to use as filename
            safe_name = filepath.replace(":", "").replace("/", "_").replace("\\", "_")
            dest = os.path.join(RESTORE_DIR, safe_name)
            shutil.copy2(filepath, dest)


def restore_file(filepath: str) -> bool:
    """Restore a file from the baseline copy. Returns True if successful."""
    safe_name = filepath.replace(":", "").replace("/", "_").replace("\\", "_")
    src = os.path.join(RESTORE_DIR, safe_name)

    if not os.path.exists(src):
        return False

    shutil.copy2(src, filepath)
    return True