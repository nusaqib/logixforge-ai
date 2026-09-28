"""PreToolUse hook: refuse Bash commands that would change a live controller unless a human opted in.

Blocks (exit 2 => tool call denied, message shown to the agent):
  lf online write ...      lf sdk download|import|import-rungs|write|mode ...
  python -m logixforge.cli online write / sdk download ...
  pycomm3 / LogixDriver write calls in inline python
unless LOGIXFORGE_ALLOW_ONLINE_WRITE=1 is set in the environment (operator decision, per session).
"""
import json
import os
import re
import sys

BLOCK_PATTERNS = [
    r"\blf\s+online\s+write\b",
    r"\blf\s+sdk\s+(download|import|import-rungs|write|mode)\b",
    r"logixforge\.cli\s+online\s+write\b",
    r"logixforge\.cli\s+sdk\s+(download|import|import-rungs|write|mode)\b",
    r"\.write\(\s*['\"(]",           # plc.write('Tag', v) inline python
    r"change_controller_mode|\.download\(",
]


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    if data.get("tool_name") != "Bash":
        return 0
    cmd = (data.get("tool_input") or {}).get("command", "")
    if not cmd:
        return 0
    if os.environ.get("LOGIXFORGE_ALLOW_ONLINE_WRITE") == "1":
        return 0
    for pat in BLOCK_PATTERNS:
        if re.search(pat, cmd):
            print(
                "LogixForge guard: this command writes to a live controller (download / tag write / mode change / "
                "partial import). It is blocked until a human confirms the machine is in a safe state and sets "
                "LOGIXFORGE_ALLOW_ONLINE_WRITE=1 for this session. Explain the intended change, the affected tags/"
                "routines and the rollback plan, then ask the operator to enable it.",
                file=sys.stderr,
            )
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
