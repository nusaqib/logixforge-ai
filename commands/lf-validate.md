---
description: Run the LogixForge validator on a project directory or .L5X and explain findings
argument-hint: <project_dir | file.L5X> [--strict]
allowed-tools: Bash, Read, Glob
---

Run `PYTHONPATH=${CLAUDE_PLUGIN_ROOT} python -m logixforge.cli validate $ARGUMENTS`.
Group findings by routine/scope, explain each error code in one line, propose the fix, and ask
whether to apply it. Codes are documented in `${CLAUDE_PLUGIN_ROOT}/standards/review-checklist.md`.
