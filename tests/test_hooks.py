import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUARD = ROOT / "hooks" / "guard_online.py"
VALIDATE = ROOT / "hooks" / "validate_on_write.py"


def run_hook(script, payload, env_extra=None):
    env = dict(os.environ)
    env.pop("LOGIXFORGE_ALLOW_ONLINE_WRITE", None)
    env["CLAUDE_PLUGIN_ROOT"] = str(ROOT)
    env.update(env_extra or {})
    return subprocess.run([sys.executable, str(script)], input=json.dumps(payload), capture_output=True, text=True, env=env)


def test_guard_blocks_online_write():
    r = run_hook(GUARD, {"tool_name": "Bash", "tool_input": {"command": "lf online write --path 10.0.0.1/0 Tag=1"}})
    assert r.returncode == 2 and "blocked" in r.stderr


def test_guard_blocks_sdk_download():
    r = run_hook(GUARD, {"tool_name": "Bash", "tool_input": {"command": "python -m logixforge.cli sdk download --acd x.ACD --path p"}})
    assert r.returncode == 2


def test_guard_allows_reads_and_optin():
    r = run_hook(GUARD, {"tool_name": "Bash", "tool_input": {"command": "lf online read --path 10.0.0.1/0 Tag"}})
    assert r.returncode == 0
    r = run_hook(GUARD, {"tool_name": "Bash", "tool_input": {"command": "lf online write --path 10.0.0.1/0 Tag=1"}},
                 {"LOGIXFORGE_ALLOW_ONLINE_WRITE": "1"})
    assert r.returncode == 0


def test_init_with_profile(tmp_path):
    r = subprocess.run([sys.executable, "-m", "logixforge.cli", "init", str(tmp_path / "p"), "--name", "X_PLC", "--profile", "alsu"],
                       capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 0, r.stderr
    assert (tmp_path / "p" / "naming.json").exists() and (tmp_path / "p" / "profile.json").exists()
    r = subprocess.run([sys.executable, "-m", "logixforge.cli", "validate", str(tmp_path / "p")], capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 0, r.stdout + r.stderr


def test_validate_on_write_reports():
    rll = ROOT / "examples" / "conveyor-demo" / "programs" / "P_Conveyor" / "routines" / "R_Outputs.rll"
    r = run_hook(VALIDATE, {"tool_name": "Write", "tool_input": {"file_path": str(rll)}})
    assert r.returncode == 0 and "LogixForge" in r.stdout
