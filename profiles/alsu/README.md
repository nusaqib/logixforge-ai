# ALS-U controls profile

Site profile for ALS-U (Advanced Light Source Upgrade, LBNL) PLC and HMI work with Studio 5000
Logix Designer and Studio 5000 View Designer. Primary platform: Allen-Bradley CompactLogix (5069)
communicating with EPICS IOCs; operator interface is CS-Studio, with PanelView HMIs as local panels.

## Status
- [x] AL-1605-0840 Rev B -> `standards/` (split by topic, spec IDs verbatim)
- [x] `naming.json` from table 8.3 (+ observed variants from masterCode: `R00_`, `_Hi_SP`, bare `Sts` members)
- [x] Reference project masterCode.L5X -> `examples/masterCode/` (0 validator errors)
- [x] Reference HMI masterHMI export -> `examples/masterCode/hmi-export/`; conventions in `standards/hmi.md`
- [x] Templates: `UDT_PermGroup` + `PermLatch_AOI` (fallback for the official ALS-U latch AOIs)
- [ ] Official ALS-U Git UDTs / DIAG_ / Latch AOIs -> `templates/`
- [ ] ALS-U Controls Alarm Philosophy AL-1692-1312 -> `standards/alarms.md`
- [ ] `examples/masterCode/hmi/hmi.json` reverse-engineered from the export (needs the .hmi reader)

## Sources
| Document | Number | Rev | Status | Loaded |
|---|---|---|---|---|
| ALS-U PLC Standardization Plan (L. Hodges) | AL-1605-0840 | B | Working draft (tracked changes, open reviewer comments) | 2026-09-28, `standards/` |
| ALS-U PLC Revision Control Workflow | AL-1605-0438 | | referenced, not loaded | |
| ALS-U Controls Alarm Philosophy | AL-1692-1312 | | referenced, not loaded (needed for alarms/HMI rules) | |
| ALS-U standard UDTs, DIAG_* and marshalling AOIs | ALS-U Controls Git | | referenced, not loaded (needed for `templates/`) | |
| Reference project masterCode (RF master interlock PLC, 5069-L320ER v36) + masterHMI View Designer export | user's Desktop / Documents | | loaded 2026-09-28 -> `examples/masterCode/` (+ `hmi-export/`) | |

When a released revision of AL-1605-0840 exists, re-check `standards/` against it; sections with
open comments in Rev B: 7 (wording of general requirements), S09-07-095290 ("separate tag").

## Layout
```
standards/          one file per topic, spec IDs (S09-07-0950xx / 0952xx-0954xx) kept verbatim
  README.md         index
  terminology.md    section 6 definitions (permit, trip, latch, first fault, bypass, ...)
  interlocks.md     section 7 permissive/mitigation/latch/first-fault behaviour + ladder pattern
  tasks-routines.md section 8.1-8.2, task and language choice
  io-tags.md        section 8.3, buffering, fail-safe outputs, UDTs, arrays, scoping, aliasing
  naming.md         section 8.4 table 8.3 naming convention
  diagnostics.md    section 8.5 DIAG_ AOIs
  documentation.md  section 9 comments and descriptions
  epics.md          section 10 PLC/IOC data transfer and alarm handling
  revision-control.md section 11
  specifications.md every spec ID in one table (section 12)
naming.json         regex per kind + tag suffix table, enforced by `lf validate` (NAME_STYLE warnings)
skeleton.json       names used by `lf init --profile alsu` (periodic task, P/R numbering)
templates/          UDT_PermGroup + PermLatch_AOI (LogixForge implementation of S09-07-095000..080;
                    replace with the official ALS-U Git AOIs when available)
examples/           reference projects (none yet)
```

## Usage
```
lf init projects/<Name> --name A0204_Vac --processor 5069-L320ER --rev 33 --profile alsu
```
Then load the `alsu-plc` / `alsu-hmi` skills; they load the generic skills and apply these standards.
