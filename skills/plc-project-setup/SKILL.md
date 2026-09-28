---
name: plc-project-setup
description: Milestone 0 for a Studio 5000 project - capture requirements into docs/SPEC.md, choose controller/firmware, define the I/O list, task/program architecture, naming rules and create the LogixForge project skeleton (controller.json, tasks.json, naming.json). Use when starting a new PLC project or onboarding an existing one.
---

# Project setup

## 1. Requirements capture -> `docs/SPEC.md`
If the user hands over documents (specifications, I/O lists, drawings, standards), ingest them first:
`python -m logixforge.cli docs ingest <dir> <file> --doc-no .. --rev ..` and read `docs/extracted/*.md`
(`plc-documentation` skill). Then interview the user for what the documents do not say and write a
functional specification with these sections, citing the source document for each requirement.
Do not write logic before the spec exists; ask focused questions for anything missing.

1. **Equipment and process**: machines, motors, valves, sensors, drives, sequences.
2. **Operating modes**: Auto / Manual / Maintenance, Local / Remote, E-stop and reset behaviour.
3. **I/O list**: table of Tag | Type (DI/DO/AI/AO/Fieldbus) | Module:Point | Signal | NO/NC | Fail-safe state.
4. **Sequences / state machines**: numbered steps with transitions, timeouts, abort paths.
5. **Interlocks and permissives**: per actuator, what must be true to start / to keep running.
6. **Alarms**: list with priority, condition, ack behaviour, HMI text.
7. **HMI interface**: which tags the HMI reads/writes (prefer one UDT per equipment item).
8. **Comms**: produced/consumed tags, MSG to other PLCs, drives on EtherNet/IP, IO-Link.
9. **Standards**: customer naming/coding standard, ISA-88 / PackML if required, safety category.
10. **Open questions** with the decision owner.

## 2. Controller choice -> `controller.json`
```json
{ "name": "LineA_PLC", "processor_type": "1756-L83E", "major_rev": 33, "minor_rev": 11,
  "software_revision": "33.00", "description": "...", "chassis_size": 10, "slot": 0, "safety": false }
```
- `processor_type`: ControlLogix `1756-L8xE(S)`, CompactLogix `5069-L3xER(MS)`, `1769-L3xER`,
  Emulate `Emulate 5570`/`Emulate 5580`. GuardLogix ends in `S`; set `"safety": true`.
- `major_rev` must match the customer's Studio 5000 version. L5X imports into equal or newer
  versions only. Ask which version they run.
- Name rules: <=40 chars, letters/digits/underscore, no double or trailing underscore.

## 3. Architecture decisions (write them in SPEC.md)
- **Tasks**: one continuous task for general logic; periodic tasks only for things that need
  determinism (PID 100 ms, fast counting 5-10 ms, motion via motion group). Safety task periodic.
- **Programs**: one per equipment/functional area (`P_Conveyor`, `P_Palletizer`, `P_Utilities`,
  `P_Alarms`, `P_Comms`). Program-scope tags by default; controller scope only for HMI interface
  UDTs, produced/consumed, cross-program data.
- **Routines per program**: `MainRoutine` (JSR list only), `R_Inputs`, `R_<Function>...`,
  `R_Alarms`, `R_Outputs`. Optional `R_Sim` for Emulate.
- **AOIs vs UDT+routine**: AOI for repeated device patterns (motor, valve, analog scaling); plain
  routines for one-off sequence logic.
- **Language**: ladder for discrete/interlock logic (maintenance staff), ST for math, strings,
  loops, state machines with many transitions; FBD for process loops if the customer prefers.

## 4. Skeleton
```
python -m logixforge.cli init <dir> --name <Controller> --processor 1756-L83E --rev 33 [--profile <site>] [--git]
```
`--git` makes the project its own repository (one repo per PLC project); `.gitignore`/`.gitattributes` are always written.
Then edit `naming.json` to the customer's convention (regex per kind) so the validator enforces it.

## 5. Definition of done for milestone 0
- SPEC.md filled, open questions listed.
- `controller.json`, `tasks.json`, `naming.json` exist; `lf validate` passes.
- Program/task/routine plan and I/O list agreed with the user.
- Every given document is in `docs/INDEX.md` with number and revision; nothing sits in `docs/input/` unindexed.
