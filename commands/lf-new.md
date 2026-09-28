---
description: Start a new Studio 5000 project with LogixForge (spec interview, skeleton, milestone plan)
argument-hint: <project_dir> <ControllerName> [processor] [major_rev]
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

Create a new LogixForge project from `$ARGUMENTS` (project dir, controller name, optional processor
type and major revision; defaults 1756-L83E / 33).

1. Run `python -m logixforge.cli init <dir> --name <Name> [--processor X] [--rev N]` with
   `PYTHONPATH=${CLAUDE_PLUGIN_ROOT}`.
2. Load the `plc-workflow` and `plc-project-setup` skills.
3. Interview the user for the functional specification (equipment, I/O, modes, sequences,
   interlocks, alarms, HMI, standards). Write `docs/SPEC.md`.
4. Propose the task/program/routine architecture and UDT/AOI inventory; get approval.
5. Update `controller.json`, `tasks.json`, `naming.json`; run `lf validate`.
6. Print the milestone plan and the next command to run.
