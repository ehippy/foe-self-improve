"""SQLite persistence for foe. Stdlib only, thread-safe via check_same_thread=False + lock."""
import os
import sqlite3
import threading

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "foe.db"
)

_lock = threading.Lock()
_conn: sqlite3.Connection | None = None

_SCHEMA = """
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    goal TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'stopped',
    pm_model TEXT,
    dev_model TEXT,
    max_iterations INTEGER NOT NULL DEFAULT 10,
    pm_review INTEGER NOT NULL DEFAULT 1,
    iterations INTEGER NOT NULL DEFAULT 0,
    note TEXT NOT NULL DEFAULT '',
    auto_publish INTEGER NOT NULL DEFAULT 1,
    publish_url TEXT NOT NULL DEFAULT '',
    published_at TEXT,
    error_message TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS iterations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL REFERENCES projects(id),
    iteration INTEGER NOT NULL,
    pm_task TEXT NOT NULL DEFAULT '',
    pm_spec TEXT NOT NULL DEFAULT '',
    dev_summary TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


def conn() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        _conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        _conn.row_factory = sqlite3.Row
        _conn.execute("PRAGMA journal_mode=WAL")
        with _lock:
            _conn.executescript(_SCHEMA)
            _conn.commit()
    return _conn


def list_projects() -> list[dict]:
    with _lock:
        rows = conn().execute("SELECT * FROM projects ORDER BY id").fetchall()
    return [dict(r) for r in rows]


def get_project(pid: int) -> dict | None:
    with _lock:
        row = conn().execute("SELECT * FROM projects WHERE id=?", (pid,)).fetchone()
    return dict(row) if row else None


def create_project(name, goal, pm_model="", dev_model="", max_iterations=10) -> int:
    with _lock:
        cur = conn().execute(
            "INSERT INTO projects (name, goal, pm_model, dev_model, max_iterations) VALUES (?,?,?,?,?)",
            (name, goal, pm_model, dev_model, max_iterations),
        )
        conn().commit()
    return cur.lastrowid


def set_status(pid: int, status: str):
    with _lock:
        conn().execute(
            "UPDATE projects SET status=?, updated_at=datetime('now') WHERE id=?",
            (status, pid),
        )
        conn().commit()


def set_note(pid: int, note: str):
    with _lock:
        conn().execute(
            "UPDATE projects SET note=?, updated_at=datetime('now') WHERE id=?",
            (note, pid),
        )
        conn().commit()


def set_publish_url(pid: int, url: str, published_at: str):
    with _lock:
        conn().execute(
            "UPDATE projects SET publish_url=?, published_at=?, updated_at=datetime('now') WHERE id=?",
            (url, published_at, pid),
        )
        conn().commit()


def set_error(pid: int, msg: str):
    with _lock:
        conn().execute(
            "UPDATE projects SET error_message=?, updated_at=datetime('now') WHERE id=?",
            (msg, pid),
        )
        conn().commit()


def increment_iterations(pid: int):
    with _lock:
        conn().execute(
            "UPDATE projects SET iterations = iterations + 1, updated_at=datetime('now') WHERE id=?",
            (pid,),
        )
        conn().commit()


def add_iteration(project_id, iteration, pm_task, pm_spec, dev_summary):
    with _lock:
        conn().execute(
            "INSERT INTO iterations (project_id, iteration, pm_task, pm_spec, dev_summary) VALUES (?,?,?,?,?)",
            (project_id, iteration, pm_task, pm_spec, dev_summary),
        )
        conn().commit()


def delete_project(pid: int):
    with _lock:
        conn().execute("DELETE FROM iterations WHERE project_id=?", (pid,))
        conn().execute("DELETE FROM projects WHERE id=?", (pid,))
        conn().commit()
