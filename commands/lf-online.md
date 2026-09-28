---
description: Guided live-controller session (read, monitor, and, after operator approval, apply a change) via pycomm3 / Logix Designer SDK
argument-hint: <cip_path or comm_path> [project_dir]
allowed-tools: Bash, Read, Glob, Grep
---

Load the `plc-live-sdk` skill. For `$ARGUMENTS`:
1. `python -m logixforge.cli online info --path <cip>` and `online tags --path <cip>`; summarise the
   controller (type, firmware, mode, forces) and confirm it matches `controller.json` if a project is given.
2. Read the tags the user cares about; present values against the spec.
3. If a change is requested: follow the standard live-change procedure in the skill. Present the
   change list and rollback plan and STOP until the operator confirms and sets
   `LOGIXFORGE_ALLOW_ONLINE_WRITE=1`. Never set that variable yourself.
