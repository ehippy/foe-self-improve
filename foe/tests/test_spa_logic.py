"""Pytest wrapper that runs the Node.js SPA logic tests via node --test."""
import subprocess
import sys
from pathlib import Path


def test_js_spa_logic_runs_and_passes():
    """Invoke node --test on the SPA logic test file and assert exit 0."""
    test_file = Path(__file__).parent / "test_spa_logic.js"
    assert test_file.exists(), f"Missing JS test file: {test_file}"

    result = subprocess.run(
        ["node", "--test", str(test_file)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, (
        f"node --test failed (exit {result.returncode})\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )
    # Sanity: the runner should report at least 4 passing tests
    assert "pass" in result.stdout.lower(), (
        f"Expected 'pass' in node --test output, got: {result.stdout}"
    )
