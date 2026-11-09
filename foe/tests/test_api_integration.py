"""Integration tests for the foe API — verifies /api/projects response structure.

Exercises the exact JSON contract the SPA's rendering logic depends on:
  - qa_status: one of 'pass' | 'fail' | 'pending'
  - qa_report: list of failure strings (empty when passing)

Run:  pytest foe/tests/test_api_integration.py -v
"""
import pytest
from fastapi.testclient import TestClient

from foe.app import app


@pytest.fixture(scope="module")
def client():
    """Create a TestClient that triggers FastAPI startup/shutdown lifecycle."""
    with TestClient(app) as c:
        yield c


def test_projects_endpoint_returns_200_list(client):
    """GET /api/projects must return 200 and a JSON array."""
    resp = client.get("/api/projects")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert isinstance(data, list), f"Expected list, got {type(data).__name__}"


def test_projects_contain_qa_status_and_qa_report(client):
    """Every project object must carry qa_status and qa_report keys.

    This is the exact contract the SPA's renderProjects() function reads:
      project.qa_status  -> badge colour (pass/fail/pending)
      project.qa_report  -> failure detail list shown in tooltip
    """
    resp = client.get("/api/projects")
    assert resp.status_code == 200
    projects = resp.json()

    for proj in projects:
        pid = proj.get("id", "?")
        assert "qa_status" in proj, (
            f"Project id={pid} is missing 'qa_status' key. "
            f"Keys present: {list(proj.keys())}"
        )
        assert "qa_report" in proj, (
            f"Project id={pid} is missing 'qa_report' key. "
            f"Keys present: {list(proj.keys())}"
        )


def test_qa_status_is_valid_enum(client):
    """qa_status must be one of the three values the SPA renders."""
    resp = client.get("/api/projects")
    assert resp.status_code == 200
    projects = resp.json()

    valid_statuses = {"pass", "fail", "pending"}
    for proj in projects:
        pid = proj.get("id", "?")
        status = proj["qa_status"]
        assert status in valid_statuses, (
            f"Project id={pid} has qa_status={status!r}, "
            f"expected one of {valid_statuses}"
        )


def test_qa_report_is_list(client):
    """qa_report must be a list (of strings) — the SPA iterates it for failure details."""
    resp = client.get("/api/projects")
    assert resp.status_code == 200
    projects = resp.json()

    for proj in projects:
        pid = proj.get("id", "?")
        report = proj["qa_report"]
        assert isinstance(report, list), (
            f"Project id={pid} qa_report is {type(report).__name__}, expected list"
        )
        for item in report:
            assert isinstance(item, str), (
                f"Project id={pid} qa_report contains non-string: {item!r}"
            )
