import hashlib
import os

def hash_file(filepath: str) -> str | None:
    """Returns SHA-256 hex digest, or None if file can't be read."""
    sha256 = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except (PermissionError, FileNotFoundError):
        return None

def hash_directory(directory: str, ignored_extensions: list) -> dict:
    """Walk a directory and hash every file. Returns {filepath: hash}."""
    hashes = {}
    for root, _, files in os.walk(directory):
        for filename in files:
            ext = os.path.splitext(filename)[1].lower()
            if ext in ignored_extensions:
                continue
            filepath = os.path.join(root, filename)
            h = hash_file(filepath)
            if h:
                hashes[filepath] = h
    return hashes