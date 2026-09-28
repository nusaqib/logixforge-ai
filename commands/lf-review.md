---
description: Full PLC code review (safety, correctness, standards) of a project or L5X using the plc-reviewer agent
argument-hint: <project_dir | file.L5X> [baseline_for_diff]
allowed-tools: Bash, Read, Glob, Grep, Agent
---

Launch the `plc-reviewer` agent on `$ARGUMENTS`. If a second path is given, include
`python -m logixforge.cli diff <baseline> <target>` output in the agent's brief so the review focuses
on the change. Relay the agent's full findings to the user, unchanged, then offer to apply fixes
(with the `plc-builder` agent) only for findings the user selects.
