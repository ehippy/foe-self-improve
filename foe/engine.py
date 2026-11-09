"""Supervisor: drives the PM ⇄ Dev loop for each running project."""
import threading
import time


class Supervisor:
    def __init__(self):
        self._threads: dict[int, threading.Thread] = {}
        self._lock = threading.Lock()

    def start(self):
        """Called on app startup — resume any 'running' projects."""
        from . import db
        for row in db.list_projects():
            if row["status"] == "running":
                self.start_project(row["id"])

    def start_project(self, pid: int):
        with self._lock:
            if pid in self._threads:
                return
            t = threading.Thread(target=self._run, args=(pid,), daemon=True)
            self._threads[pid] = t
            t.start()

    def _run(self, pid: int):
        """Main loop for a single project. Placeholder — real logic in full build."""
        from . import db
        while True:
            row = db.get_project(pid)
            if row is None or row["status"] != "running":
                break
            # In a full implementation this would call litellm for PM and Dev.
            # For this QA-focused task we just sleep to keep the thread alive.
            time.sleep(2)
        self._threads.pop(pid, None)
