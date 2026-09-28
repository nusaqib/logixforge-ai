---
name: alsu-plc
description: ALS-U (LBNL Advanced Light Source Upgrade) site profile for Studio 5000 PLC work - applies the ALS-U controls guideline (naming, program structure, interlocks, alarms, I/O, safety, deliverables) on top of the generic LogixForge milestone skills. Use for any PLC task on an ALS-U system or when the user mentions ALS-U, ALS, LBNL, accelerator, beamline, vacuum, or the ALS-U guideline.
---

# ALS-U PLC profile

Profile root: `${CLAUDE_PLUGIN_ROOT}/profiles/alsu/`. Read its `README.md` first; it lists which
guideline sections have been loaded. Where the profile is silent, the generic skills apply.

## Procedure
1. Load `plc-workflow`, then the generic skill for the milestone you are on.
2. Read the matching profile standard: `profiles/alsu/standards/<topic>.md`
   (naming, coding, io, alarms, safety, deliverables). Profile rules **override** generic ones.
3. New projects: `python -m logixforge.cli init <dir> --name <Ctrl> --profile alsu`
   (copies `naming.json` and `templates/`). Existing projects: copy `profiles/alsu/naming.json` in.
4. Reuse before inventing: check `profiles/alsu/templates/` (UDTs, AOIs) and
   `profiles/alsu/examples/` (reference projects) for an existing pattern; match its style exactly.
5. In reports, cite the guideline section for every profile-driven decision ("per ALS-U naming 3.2").

## Until the guideline is loaded
The profile is a scaffold: `naming.json` mirrors the generic standard and `standards/` has only the
topic index. Say so explicitly, follow the generic standards, and list the places where the ALS-U
guideline will need to be applied later (naming, alarm severities, HMI colours, safety procedure).
