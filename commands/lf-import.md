---
description: Bring a Studio 5000 L5X export (or controller upload) into a LogixForge spec and diff it against the repo
argument-hint: <export.L5X> <spec_dir>
allowed-tools: Bash, Read, Glob, Write
---

For `$ARGUMENTS` (L5X path, target spec dir):
1. `PYTHONPATH=${CLAUDE_PLUGIN_ROOT} python -m logixforge.cli decompile <export.L5X> -o <spec_dir>.incoming`
2. `python -m logixforge.cli diff <spec_dir> <spec_dir>.incoming`
3. Summarise the differences (routines, tags, UDTs). Ask which direction wins per item, then merge
   into `<spec_dir>` by copying files from `.incoming` or keeping the repo version.
4. `lf validate <spec_dir>` and report.
