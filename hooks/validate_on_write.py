"""PostToolUse hook: after the agent writes/edits a project spec file or an .L5X, run the validator
and feed findings back so mistakes are caught immediately (rung syntax, unknown tags, naming).

Only errors/warnings are reported. Exit 0 always (advisory), output goes to the agent as context.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

SPEC_HINTS = {".rll", ".st", ".fbd", ".l5x"}
SPEC_JSON = {"controller.json", "tasks.json", "tags.json", "program.json", "aoi.json", "modules.json", "naming.json"}


def project_root(p: Path):
    for parent in [p] + list(p.parents):
        if (parent / "controller.json").exists():
            return parent
    return None


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    fp = (data.get("tool_input") or {}).get("file_path", "")
    if not fp:
        return 0
    p = Path(fp)
    ext = p.suffix.lower()
    is_spec = ext in SPEC_HINTS or p.name in SPEC_JSON or (ext == ".json" and p.parent.name in {"datatypes", "tags", "modules"})
    if not is_spec:
        return 0
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", str(Path(__file__).resolve().parents[1]))
    target = str(p) if ext == ".l5x" else project_root(p)
    if not target:
        return 0
    env = dict(os.environ, PYTHONPATH=plugin_root + os.pathsep + os.environ.get("PYTHONPATH", ""))
    r = subprocess.run([sys.executable, "-m", "logixforge.cli", "validate", str(target)], capture_output=True, text=True, env=env)
    lines = [l for l in (r.stdout + r.stderr).splitlines() if l.startswith(("[ERROR", "[WARNING", "spec error"))]
    if lines:
        print("LogixForge validation after edit of " + p.name + ":\n" + "\n".join(lines[:40]))
    else:
        print(f"LogixForge: {p.name} validated clean (no errors/warnings).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
