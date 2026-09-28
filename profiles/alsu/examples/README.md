# ALS-U reference projects

Each subfolder is a real ALS-U project as a LogixForge spec, used by the skills as the worked example
and by the reviewer as the style reference.

To add one:
```
# PLC: Studio 5000 > File > Save As > .L5X
lf decompile <export.L5X> -o profiles/alsu/examples/<project>
# HMI: View Designer > File > Export Project, copy the folder to
#      profiles/alsu/examples/<project>/hmi-export/   (raw .hmi files, reference for syntax and layout)
lf validate profiles/alsu/examples/<project>
```
Remove or anonymise anything that must not be in the repository (IP addresses, credentials, drawings).

## masterCode (loaded 2026-09-28)
RF master interlock PLC (5069-L320ER, Logix v36): LLRF1/2, cavities, tuners (AMCI stepper AOIs), arc
detectors, HP coax switches, PPS/MPS interfaces, EPICS interface UDTs. Programs `P000_Master_Interlock`,
`P010_Device_Control`, `PowerUpProgram`; latch/first-fault AOIs `Latch_AOI`, `Latch_bi_AOI`, `Latch_ai_AOI`,
`FF_AOI`; `Module_Status_AOI`. `hmi-export/` is the matching View Designer project (PanelView 5510).
Contains lab IP addresses in `modules/*.xml` and `hmi-export/Devices/masterCode.hmi`; keep the repository
internal or scrub them before publishing. `lf validate profiles/alsu/examples/masterCode` = 0 errors;
warnings show where the real code departs from AL-1605-0840 (descriptions, naming suffixes).
`docs/generated/` is the as-built document set from `lf docs build` (the `plc-document-existing` output for a real project).
