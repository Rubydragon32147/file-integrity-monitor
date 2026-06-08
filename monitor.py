import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from hasher import hash_file
from logger import log_alert

class IntegrityHandler(FileSystemEventHandler):
    def __init__(self, baseline: dict, config: dict):
        self.baseline = baseline
        self.config = config

    def _should_ignore(self, path: str) -> bool:
        import os
        ext = os.path.splitext(path)[1].lower()
        return ext in self.config["ignored_extensions"]

    def on_modified(self, event):
        if event.is_directory or self._should_ignore(event.src_path):
            return
        path = event.src_path
        new_hash = hash_file(path)
        old_hash = self.baseline.get(path)

        if old_hash and new_hash and new_hash != old_hash:
            log_alert({"type": "MODIFIED", "path": path, "old_hash": old_hash, "new_hash": new_hash})
            self.baseline[path] = new_hash  # update in-memory baseline

    def on_deleted(self, event):
        if event.is_directory or self._should_ignore(event.src_path):
            return
        path = event.src_path
        if path in self.baseline:
            log_alert({"type": "DELETED", "path": path, "old_hash": self.baseline[path], "new_hash": None})
            del self.baseline[path]

    def on_created(self, event):
        if event.is_directory or self._should_ignore(event.src_path):
            return
        path = event.src_path
        new_hash = hash_file(path)
        if new_hash:
            log_alert({"type": "NEW", "path": path, "old_hash": None, "new_hash": new_hash})
            self.baseline[path] = new_hash


def start_monitor(baseline: dict, config: dict):
    """Start watchdog observer on all configured paths."""
    handler = IntegrityHandler(baseline, config)
    observer = Observer()
    for path in config["watch_paths"]:
        observer.schedule(handler, path, recursive=True)
    observer.start()
    return observer