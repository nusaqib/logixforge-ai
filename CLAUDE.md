# LogixForge - repo guidance for Claude Code

This repo is both a Claude Code **plugin** (skills/agents/commands/hooks) and a Python **toolkit**
(`logixforge/`). Start any PLC task by loading the `plc-workflow` skill.

## Commands
- Tests: `python -m pytest -q`
- Validate/build demo: `python -m logixforge.cli validate examples/conveyor-demo` and
  `python -m logixforge.cli build examples/conveyor-demo --partials`
- Run the plugin in dev mode: `claude --plugin-dir .`

## Conventions
- Toolkit is stdlib-only; `mcp`, `pycomm3`, Logix Designer SDK are optional imports inside functions.
- Never generate module `<Module>` XML by hand; it comes from Studio 5000 exports.
- Add a validator rule = add a code to `standards/review-checklist.md` and a test in `tests/`.
- Skills are short and imperative; long references live in `standards/`.
- Anything that writes to a live controller goes through `require_write_permission()` and is
  matched by `hooks/guard_online.py`.
- `build/` output is generated and git-ignored; the spec is the source of truth. `docs/generated/` is also generated
  (`lf docs build`) but committed; never hand-edit it. Given documents go through `lf docs ingest`.
- Real PLC projects live in their own repositories (`lf init --git`); this repo keeps only `examples/` and `profiles/`.
- Site-specific rules live in `profiles/<name>/` plus thin `skills/<name>-plc` / `<name>-hmi` skills that
  load the generic skill first. Never bake site rules into the generic skills or the validator defaults.
