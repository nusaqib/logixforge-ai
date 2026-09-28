# All ALS-U PLC specifications (AL-1605-0840 Rev B, sections 7 and 12)

ID format SYY-XX-QQQQQQ (section 4.2); IDs are never reassigned. Strength: shall = binding, should = goal.

| Spec ID | Strength | Specification | Topic file |
|---|---|---|---|
| S09-07-095000 | shall | All permissives normal -> mitigation output permit/normal (subject to 095020, 095040) | interlocks |
| S09-07-095010 | shall | Any permissive trips -> mitigation output inhibit | interlocks |
| S09-07-095020 | shall | Trip state held after condition clears until operator reset (and possibly restart) | interlocks |
| S09-07-095030 | shall | Permissive trip -> its latch set to trip | interlocks |
| S09-07-095040 | shall | Latch stays tripped until operator latch reset | interlocks |
| S09-07-095050 | shall | First-fault set for the first tripped permissive | interlocks |
| S09-07-095060 | shall | On a trip event all other first-fault signals set to normal | interlocks |
| S09-07-095070 | shall | First fault held until reset or a subsequent trip event | interlocks |
| S09-07-095080 | will | First-fault signals reset on each trip event; use logs for history | interlocks |
| S09-07-095200 | should | Continuous task only for simple programs without task coordination | tasks-routines |
| S09-07-095210 | should | Continuous task for housekeeping (alarm handling, EPICS comms) | tasks-routines |
| S09-07-095220 | should | Periodic tasks are the default | tasks-routines |
| S09-07-095230 | shall | Periodic tasks when coordination between tasks is necessary | tasks-routines |
| S09-07-095240 | shall | Event task only when fastest response is required | tasks-routines |
| S09-07-095250 | shall | Event tasks do not share outputs with other tasks | tasks-routines |
| S09-07-095260 | should | Ladder for interlock, pushbutton, combinatorial logic | tasks-routines |
| S09-07-095270 | should | ST for AOI calls, parameterised functions, iterative/complex logic | tasks-routines |
| S09-07-095280 | should | FBD considered for analog processing, ramp-soak, PID | tasks-routines |
| S09-07-095290 | shall | Inputs buffered into a separate tag before use | io-tags |
| S09-07-095300 | shall | Output modules/data configured to a known fail-safe state on fault | io-tags |
| S09-07-095310 | shall | Non-zero fault outputs documented in subsystem design docs | io-tags |
| S09-07-095320 | should | UDTs organise tags | io-tags |
| S09-07-095330 | should | Marshalling encapsulated in AOIs / parameterised functions | io-tags |
| S09-07-095340 | shall | EPICS-accessed tags are controller tags | io-tags |
| S09-07-095350 | should | Program tags when not needed outside the program | io-tags |
| S09-07-095360 | shall | Tags named or aliased meaningfully | io-tags, naming |
| S09-07-095370 | should | Controller tag names resemble EPICS names | naming |
| S09-07-095380 | shall | Use the standard AOIs for buffering and module health | diagnostics |
| S09-07-095390 | will | Diagnostic AOIs maintained in ALS-U Git | diagnostics |
| S09-07-095400 | shall | Rungs/lines/FBDs commented with their necessity | documentation |
| S09-07-095410 | should | Comments reference governing documents | documentation |
| S09-07-095420 | should | Boolean descriptions define signal states | documentation |
| S09-07-095430 | should | EPICS input data packaged as array tags | epics |
| S09-07-095440 | shall | Array tags under 500 bytes | epics |
| S09-07-095450 | shall | EPICS output data as individual tags | epics |
| S09-07-095460 | will | IOC-accessed tags documented in the standard spreadsheet | epics |
| S09-07-095470 | shall | Use the ALS-U PLC revision control process | revision-control |
