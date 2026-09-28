---
name: plc-workflow
description: Entry point for any Rockwell Studio 5000 / Logix PLC programming task. Use when the user asks to design, write, extend, review, or deploy ControlLogix/CompactLogix code (ladder, structured text, AOIs, UDTs, tags, tasks, I/O, L5X import/export, live controller work). Routes to the milestone skills in the right order and enforces the build/validate loop.
---

# LogixForge workflow

You are programming a Rockwell Logix controller. Work **milestone by milestone** and keep the
project as a text spec that `lf build` turns into L5X. Never hand-write L5X XML; write the spec.

## Where things live
- Toolkit CLI: `python -m logixforge.cli` (alias `lf` if installed). Run from `${CLAUDE_PLUGIN_ROOT}`
  or with `PYTHONPATH=${CLAUDE_PLUGIN_ROOT}`.
- Project spec layout (see `plc-project-setup`):
  `controller.json`, `datatypes/*.json`, `aois/<AOI>/aoi.json + routines/Logic.rll`, `tags/*.json`,
  `modules/*.xml`, `programs/<P>/{program.json,tags.json,routines/*.rll|*.st}`, `tasks.json`, `alarms.json`,
  `hmi/hmi.json`, `naming.json`, `docs/{INDEX.md,SPEC.md,input/,extracted/,generated/}`.
- Standards: `${CLAUDE_PLUGIN_ROOT}/standards/` (naming, coding, review checklist, L5X and instruction references).
- Worked example: `${CLAUDE_PLUGIN_ROOT}/examples/conveyor-demo`.

## Milestone order (each has a skill)
| # | Milestone | Skill | Output |
|---|---|---|---|
| 0 | Requirements and architecture | `plc-project-setup` | `docs/SPEC.md`, `controller.json`, I/O list, task plan |
| 1 | Data types | `plc-udts` | `datatypes/*.json` |
| 2 | Add-On Instructions | `plc-aoi` | `aois/*/` |
| 3 | Tags | `plc-tags` | `tags/*.json`, `programs/*/tags.json` |
| 4 | I/O modules | `plc-io-modules` | `modules/*.xml` + alias tags |
| 5 | Programs and tasks | `plc-programs-tasks` | `programs/*/program.json`, `tasks.json` |
| 6 | Ladder routines | `plc-ladder` | `routines/*.rll` |
| 7 | Structured Text routines | `plc-structured-text` | `routines/*.st` |
| 8 | Safety (GuardLogix) | `plc-safety` | safety task/program/tags |
| 9 | Review | `plc-review` | findings, fixes |
| 10 | Export / import into Studio 5000 | `plc-export-import` | `build/*.L5X` |
| 11 | Test | `plc-testing` | test plan, Emulate/pycomm3 scripts |
| 12 | Live controller work | `plc-live-sdk` | guarded online changes |
| 13 | Alarms | `plc-alarms` | `alarms.json` (tag-based alarm conditions) |
| 14 | HMI | `hmi-view-designer` | `hmi/hmi.json` -> View Designer import folder (`lf hmi build`), HMI docs |
| 15 | HMI (FactoryTalk/Optix, roadmap) | `hmi-factorytalk` | tag interface + alarm CSV hand-off |
| 16 | Documentation (in and out) | `plc-documentation` | `docs/INDEX.md` + `docs/extracted/` from given documents; `docs/generated/` from the spec (`lf docs build`) |
| 17 | Document an existing project (ACD/L5X + HMI export) | `plc-document-existing` | `<name>_docs/` or a full spec repo with as-built SPEC.md |

Site profiles: if the project has `profile.json` or the user names a site (e.g. ALS-U), also load
`skills/<profile>-plc` / `<profile>-hmi`; their rules override the generic ones.

Small change requests do not need every milestone: identify which files change, edit them, then
always run the loop below.

## The loop (after every edit)
```
python -m logixforge.cli validate <project_dir>      # must be 0 errors; fix warnings or justify them
python -m logixforge.cli build <project_dir> --partials
python -m logixforge.cli inspect <project_dir>/build/<Name>.L5X
python -m logixforge.cli docs build <project_dir>    # keep docs/generated in step with the spec (DOC_STALE otherwise)
```
The PostToolUse hook runs `validate` automatically after you write spec files; read its output.

## Non-negotiables
1. **Safety first.** Outputs that move equipment are gated by safety/permissive conditions in the
   output-mapping routine. Never bypass an interlock to "make it work". Never write to a live
   controller without an explicit operator go-ahead (the guard hook enforces this).
2. **Deterministic naming** per `standards/naming-conventions.md` and the project's `naming.json`.
3. **Every tag, member, parameter, rung group and routine has a description.** Descriptions are
   what the next engineer (and the HMI/alarm system) sees.
4. **One output, one place.** A given OTE/tag is driven from exactly one rung/statement.
5. **Inputs mapped in, outputs mapped out.** Logic works on program tags, not raw I/O.
6. **Spec is the source of truth**, `build/` is generated. Commit the spec, not the L5X (unless
   the customer requires the L5X in VCS as well).
7. Say clearly what has been verified by tooling versus what still needs Studio 5000 (import,
   verify/compile, Emulate run). LogixForge cannot compile Logix code.

## Reporting to the user
End each milestone with: files written, validator result, what is NOT yet done, and the exact
Studio 5000 steps (if any) they need to take next.
