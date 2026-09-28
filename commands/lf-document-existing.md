---
description: Generate as-built documentation for an existing Studio 5000 project from its .L5X export (and optional HMI export)
argument-hint: <export.L5X> [output_dir | --onboard <repo_dir>]
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

Load the `plc-document-existing` skill (and the site profile skill if the user names one).

1. If `$ARGUMENTS` is an .ACD, ask the user to save it as .L5X first (Studio 5000: File > Save As > L5X).
2. Docs only: `PYTHONPATH=${CLAUDE_PLUGIN_ROOT} python -m logixforge.cli validate <export.L5X>` then
   `PYTHONPATH=${CLAUDE_PLUGIN_ROOT} python -m logixforge.cli docs build <export.L5X> [-o <dir>]`.
   Onboard (`--onboard <repo>`): `lf decompile <export.L5X> -o <repo>`, then `lf validate <repo>`, `lf docs ingest <repo> <export.L5X> --no-copy`, `lf docs build <repo>`.
3. Read the generated `ROUTINES.md` and `INTERLOCKS.md`, inspect every routine
   (`lf inspect <export> --routine P/R`), and write the as-built `SPEC.md` per the skill (inferred statements marked).
4. Report: Logix version, counts, generated files, review findings by severity, open questions.
