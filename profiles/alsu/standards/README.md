# ALS-U standards index (from AL-1605-0840 Rev B, working draft)

| File | Source section | Use it for |
|---|---|---|
| terminology.md | 6 | vocabulary in tag descriptions, comments, HMI text |
| interlocks.md | 7 (S09-07-095000..095080) | any permissive / trip / latch / first-fault / reset logic |
| tasks-routines.md | 8.1, 8.2 (S09-07-095200..095280) | task architecture, choosing LD / ST / FBD |
| io-tags.md | 8.3 (S09-07-095290..095370) | input buffering, fail-safe outputs, UDTs, arrays, tag scope, aliases |
| naming.md | 8.4 table 8.3 | every name: CPU, racks, modules, tasks, programs, routines, AOIs, UDTs, tags |
| diagnostics.md | 8.5 (S09-07-095380..095390) | module health monitoring, DIAG_ AOIs |
| documentation.md | 9 (S09-07-095400..095420) | rung comments, tag descriptions |
| epics.md | 10 (S09-07-095430..095460) | what EPICS can read, array packaging, alarm ownership |
| revision-control.md | 11 (S09-07-095470) | Git + Logix Designer Compare Tool workflow |
| specifications.md | 12 | all spec IDs with shall/should strength, for citing in reviews |

Wording strength (section 4.1): **shall** = binding, **should**/**may** = goal, **will** = statement of intent.
The plan is a guideline: subsystem engineers may deviate with documented justification in the
subsystem specification (section 5). Record deviations in the project's `docs/SPEC.md`.
