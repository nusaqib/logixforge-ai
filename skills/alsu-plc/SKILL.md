---
name: alsu-plc
description: ALS-U (LBNL Advanced Light Source Upgrade) site profile for Studio 5000 PLC work - applies the ALS-U PLC Standardization Plan AL-1605-0840 (permissive/latch/first-fault interlocks, periodic-task default, input buffering, EPICS-facing controller tags and arrays, T##/P##/R## and _Sts/_Ltch/_FF/_Cmd naming, DIAG_ AOIs, documentation) on top of the generic LogixForge milestone skills. Use for any PLC task on an ALS-U system or when the user mentions ALS-U, ALS, LBNL, accelerator, beamline, RF, vacuum, PPS/MPS, EPICS, or the ALS-U guideline.
---

# ALS-U PLC profile

Profile root: `${CLAUDE_PLUGIN_ROOT}/profiles/alsu/`. Source: AL-1605-0840 Rev B (working draft) split
into `standards/*.md`; every rule carries its spec ID (S09-07-0950xx / 0952xx-0954xx). Where the
profile is silent, the generic skills apply. Reference project: `examples/masterCode/` (5069-L320ER,
v36, RF master interlock PLC) - match its style for anything the guideline leaves open.

## Procedure
1. Load `plc-workflow`, then the generic skill for the milestone; then read the matching profile file:
   `standards/interlocks.md` (any permissive/trip logic), `tasks-routines.md`, `io-tags.md`, `naming.md`,
   `diagnostics.md`, `documentation.md`, `epics.md`, `revision-control.md`. `specifications.md` lists all IDs.
2. New projects: `python -m logixforge.cli init <dir> --name <CPU> --processor 5069-L320ER --rev 36 --profile alsu`
   (periodic `T100_Main`, `P100_Main`, `R000_MainRoutine`, `R005_IO_Buffering`, `naming.json`, templates).
   Existing projects: copy `profiles/alsu/naming.json` in. Start `docs/SPEC.md` from `templates/docs/SPEC.template.md`.
3. Cite the spec ID for every profile-driven decision in comments and reports ("per S09-07-095290").
4. Deviations are allowed (section 5) but must be recorded in `docs/SPEC.md` section 9 with justification.

## Rules that change the generic defaults
- **Interlocks** (S09-07-095000..080): per permissive `_Sts` (1 = normal), `_Byp`, `_Ltch`, `_FF`; group
  `_Rst` and mitigation `_Out`. Latch on trip, hold until operator reset with the signal normal, first fault
  only for the first trip of an event, bypass = permit. Use the official ALS-U latch AOIs from ALS-U Git
  (`Latch_AOI`, `Latch_bi_AOI`, `Latch_ai_AOI`, `FF_AOI` in masterCode; `biLatch_AOI` in the doc); the
  template `PermLatch_AOI` + `UDT_PermGroup` is the fallback implementation of the same spec.
- **Tasks**: periodic by default (S09-07-095220), continuous only for housekeeping/EPICS comms; event
  tasks never share outputs. Numbering `T##` by 10s, `P##`/`R##` by 5s.
- **Inputs are buffered** before use (S09-07-095290) - `R005_IO_Buffering` / DIAG_ AOIs run first;
  control logic never touches `Local:x:I`. Output modules fail-safe to zero (S09-07-095300/310).
- **Scope**: controller tags only for EPICS-facing data (non-UDT, S09-07-095340); EPICS inputs packed
  into arrays < 500 bytes (S09-07-095430/440); EPICS outputs as individual tags (S09-07-095450).
  UDTs organise everything else; marshalling in AOIs (S09-07-095330).
- **Language**: ladder for interlocks/pushbuttons; ST for AOI calls, loops, complex logic; FBD for analog/PID.
- **Naming** (`naming.md`, enforced as NAME_STYLE/NAME_SUFFIX warnings): `T100_IO_Buffering`,
  `P100_AR01_Interlocks`, `R000_MainRoutine`, `biLatch_AOI`, `DIAG_IB16`, `UDT_LLRF`/`MainUDT_`,
  tags EPICS-like + suffix (`AR01C_VVR1_Opn_Cmd`, `_Val`, `_SP`, `_HH_SP`, `_Tmr`, `_OSS`), buffers `R01S03AI[3]`.
- **Documentation**: comments explain necessity and cite the governing document; BOOL descriptions
  define both states ("1 = Ok, 0 = Trip") (S09-07-095400..420).
- **Alarms**: EPICS owns alarms; the PLC owns setpoints (`_H_SP` etc.). `alarms.json` is for the local
  PanelView only. Revision control per AL-1605-0438 (Git + Logix Designer Compare Tool).

## Toolkit notes for ALS-U projects
- Target firmware v36 exports rung text with `MOVE/EQ/GT/GE/LT/LE/LIMIT`; write `MOV/EQU/...` or the
  new names, both validate. Module-defined types (`_000A:...:O:0`) and `PowerLossProgram` are supported.
- `lf validate` on `examples/masterCode` is the regression check for the profile rules.
