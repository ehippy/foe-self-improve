"""foe — adversarial PM ⇄ developer loop. FastAPI + Bootstrap, multi-project."""
import os
import re
import json

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from . import db, engine, publish

app = FastAPI(title="foe", version="0.1.0")
STATIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


class ProjectIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    goal: str = Field(min_length=1)
    pm_model: str = ""
    dev_model: str = ""
    max_iterations: int = Field(default=10, ge=1, le=100)
    start: bool = True


class NoteIn(BaseModel):
    note: str = Field(max_length=2000)


@app.on_event("startup")
def _start_supervisor():
    db.conn()
    engine.Supervisor().start()


@app.get("/")
def index():
    path = os.path.join(STATIC, "index.html")
    if not os.path.isfile(path):
        raise HTTPException(status_code=500, detail="static/index.html missing")
    return FileResponse(path, media_type="text/html")


def _derive_qa_status(pid: int) -> tuple:
    """Derive qa_status and qa_report from the latest QA JSON for a project."""
    qa_dir = os.path.join(DATA_DIR, "qa", str(pid))
    if not os.path.isdir(qa_dir):
        return ("pending", [])
    # Find the latest iteration file
    files = [f for f in os.listdir(qa_dir) if f.endswith(".json")]
    if not files:
        return ("pending", [])
    # Sort by iteration number
    def _iter_num(fname):
        m = re.match(r"iter(\d+)\.json$", fname)
        return int(m.group(1)) if m else 0
    files.sort(key=_iter_num, reverse=True)
    latest = files[0]
    path = os.path.join(qa_dir, latest)
    try:
        with open(path, "r") as fh:
            data = json.load(fh)
    except (json.JSONDecodeError, OSError):
        return ("pending", [])
    if data.get("ok"):
        return ("pass", [])
    else:
        failures = data.get("failures", [])
        return ("fail", failures)


def _project_dict(row) -> dict:
    """Convert a project row to a JSON-serialisable dict with QA fields."""
    d = dict(row)
    qa_status, qa_report = _derive_qa_status(d["id"])
    d["qa_status"] = qa_status
    d["qa_report"] = qa_report
    return d


@app.get("/api/projects")
def list_projects():
    rows = db.list_projects()
    return [_project_dict(r) for r in rows]


@app.post("/api/projects")
def create_project(body: ProjectIn):
    pid = db.create_project(
        name=body.name,
        goal=body.goal,
        pm_model=body.pm_model,
        dev_model=body.dev_model,
        max_iterations=body.max_iterations,
    )
    if body.start:
        db.set_status(pid, "running")
    return {"id": pid, "status": "running" if body.start else "stopped"}


@app.get("/api/projects/{pid}")
def get_project(pid: int):
    row = db.get_project(pid)
    if row is None:
        raise HTTPException(status_code=404, detail="project not found")
    return _project_dict(row)


@app.post("/api/projects/{pid}/start")
def start_project(pid: int):
    row = db.get_project(pid)
    if row is None:
        raise HTTPException(status_code=404, detail="project not found")
    db.set_status(pid, "running")
    return {"id": pid, "status": "running"}


@app.post("/api/projects/{pid}/stop")
def stop_project(pid: int):
    row = db.get_project(pid)
    if row is None:
        raise HTTPException(status_code=404, detail="project not found")
    db.set_status(pid, "stopped")
    return {"id": pid, "status": "stopped"}


@app.post("/api/projects/{pid}/publish")
def publish_project(pid: int):
    row = db.get_project(pid)
    if row is None:
        raise HTTPException(status_code=404, detail="project not found")
    if row["status"] != "done":
        raise HTTPException(status_code=409, detail="project must be in done status to publish")
    result = publish.publish_project(pid)
    return result


@app.post("/api/projects/{pid}/qa")
def run_qa(pid: int):
    row = db.get_project(pid)
    if row is None:
        raise HTTPException(status_code=404, detail="project not found")
    qa_status, qa_report = _derive_qa_status(pid)
    return {"qa_status": qa_status, "qa_report": qa_report}


@app.post("/api/projects/{pid}/note")
def set_note(pid: int, body: NoteIn):
    db.set_note(pid, body.note)
    return {"ok": True}


@app.get("/api/projects/{pid}/iterations")
def list_iterations(pid: int):
    return db.list_iterations(pid)
