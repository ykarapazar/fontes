"""plugin/, .claude-plugin/marketplace.json and server.json match the code (pinned version, host list)."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_plugin_bundle_is_fresh():
    r = subprocess.run([sys.executable, "scripts/plugin_bundle.py", "--check"], cwd=ROOT,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + "\nrun: uv run python scripts/plugin_bundle.py"
