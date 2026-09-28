---
name: plc-export-import
description: Milestone 10 - produce L5X files from a LogixForge project (full controller or partial import of routines/programs/tags/UDTs/AOIs), import them into Studio 5000, handle collisions, version compatibility, and bring Studio 5000 exports back into the spec (decompile). Use for any L5X/L5K/ACD exchange question.
---

# Export and import (L5X)

## Build
```
python -m logixforge.cli build <project> [--partials] [-o out.L5X]
python -m logixforge.cli partial <project> --kind Routine --name R_Conveyor --program P_Conveyor
python -m logixforge.cli partial <project> --kind AddOnInstructionDefinition --name AOI_Motor
python -m logixforge.cli partial <project> --kind DataType --name UDT_Motor
python -m logixforge.cli partial <project> --kind Program  --name P_Conveyor
python -m logixforge.cli partial <project> --kind Tag --name HMI_Conveyor01 [--program P]
```
Build refuses on validation errors (`--force` to override for debugging).

## Into Studio 5000
**Full project** (`TargetType="Controller"`): File > Open > select the `.L5X`; Studio creates an
`.ACD`. Use for new projects.
**Partial import** (`ContainsContext="true"`): in the Controller Organizer right-click the matching
folder (Data Types, Add-On Instructions, Tags, Program, Routines) > **Import...** > pick the file.
The Import Configuration dialog lists collisions per item:
- *Use Existing* keeps the project's version, *Overwrite* replaces, *Discard* skips, *Create* renames.
- Tags referenced by imported rungs but missing are created with the type in the file (LogixForge
  puts referenced program tags in the routine's context only for `Program` imports; for `Routine`
  imports create tags first via a `Tag`/`Program` import or have Studio create them as `Undefined`
  and fix types).
- Import is offline or online (online adds to pending edits, then Accept > Test > Assemble).

**Rung-level import** (paste): open the `.rll` file, copy rung text, right-click a rung in Studio >
Paste; Studio parses neutral text directly. Fastest for a single rung fix.

## Version compatibility
- `SoftwareRevision` in the file <= installed Studio version; set `major_rev` to the customer's.
- v21 -> v24+ changed program parameters; v32 added USINT/UDINT; v31+ `AlarmDefinitions`; v34
  Logix Designer SDK; v36 new tag-based alarms. Keep generated features within the target version.
- L5K (text) is not produced; Studio can convert L5X <-> L5K if a tool needs it.

## Back from Studio 5000
Export project: File > Save As > `.L5X`. Then
```
python -m logixforge.cli decompile <export.L5X> -o <new_spec_dir>
python -m logixforge.cli diff <spec_dir> <export.L5X>
```
Decompile writes an editable spec (routines as `.rll`/`.st`, tags/UDTs/AOIs as JSON, modules as XML).
Use this to onboard legacy projects and to reconcile online edits back into the repo.

## What LogixForge verified vs what Studio verifies
LogixForge checks structure, names, references, operand counts, ST block balance. Studio 5000 checks
data-type compatibility of operands, instruction semantics, I/O, and compiles. Always state that the
project must be **verified in Studio 5000 (Logic > Verify Controller)** before download.
