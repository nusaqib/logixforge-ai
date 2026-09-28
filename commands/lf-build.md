---
description: Validate and build the L5X (plus partial import files) for a LogixForge project
argument-hint: [project_dir]
allowed-tools: Bash, Read, Glob
---

Build the project in `$ARGUMENTS` (default: the directory containing `controller.json` nearest the
current working directory).

```
PYTHONPATH=${CLAUDE_PLUGIN_ROOT} python -m logixforge.cli validate <dir>
PYTHONPATH=${CLAUDE_PLUGIN_ROOT} python -m logixforge.cli build <dir> --partials
PYTHONPATH=${CLAUDE_PLUGIN_ROOT} python -m logixforge.cli inspect <dir>/build/<Name>.L5X
```
If validation fails, fix the spec (load the relevant milestone skill), do not use `--force`.
Report: output paths, validator summary, and the exact Studio 5000 import steps from the
`plc-export-import` skill for what was built.
