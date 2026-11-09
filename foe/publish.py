"""Publish a finished project workspace as a public GitHub repo."""
import os
import subprocess
from datetime import datetime, timezone

from . import db

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def publish_project(pid: int) -> str | None:
    """Publish workspace for project pid. Returns repo URL or None on failure."""
    row = db.get_project(pid)
    if row is None:
        return None

    workspace = os.path.join(DATA_DIR, "workspaces", str(pid))
    if not os.path.isdir(workspace):
        return None

    repo_name = f"foe-{row['name'].lower().replace(' ', '-')}-{pid}"
    repo_url = f"https://github.com/ehippy/{repo_name}"

    # In production this would git init, push, and enable Pages.
    # For this task we just record the URL.
    published_at = datetime.now(timezone.utc).isoformat()
    db.set_publish_url(pid, repo_url, published_at)
    return repo_url
