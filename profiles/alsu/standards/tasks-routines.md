# Tasks and routine types (AL-1605-0840 sections 8.1, 8.2)

## Tasks
| Spec ID | Requirement |
|---|---|
| S09-07-095200 | The Continuous Task should only be used for simple programs, and when coordination with other tasks is not necessary. |
| S09-07-095210 | The Continuous Task should be used for basic housekeeping tasks such as alarm handling and EPICS communication. |
| S09-07-095220 | **Periodic tasks should be treated as the default** for PLC programming. |
| S09-07-095230 | Periodic tasks shall be used when coordination between program tasks is necessary. |
| S09-07-095240 | An Event Task shall only be used when the fastest response is required. |
| S09-07-095250 | Event Tasks shall not share outputs with other tasks. |

Guidance from 8.1: modern PLCs are soft real-time; scheduling is best-effort and priority based.
There is nothing to gain evaluating logic faster than the physical system responds. Choose periods
from the process, not from the CPU. Diagnostic/buffering code (diagnostics.md) is scheduled to run
**before** control logic and possibly at a higher frequency.

LogixForge default for ALS-U (`skeleton.json`): one periodic task `T100_Main` (100 ms) for control,
`T050_IO_Buffering` faster if DIAG_/buffer AOIs are used, optional continuous `T900_Housekeeping`
for EPICS marshalling and alarm setpoint handling. Numbers skip by 10s (tasks) and 5s (programs,
routines) so items can be inserted later (naming.md).

## Routine types
| Spec ID | Requirement |
|---|---|
| S09-07-095260 | Ladder Diagram should be used for interlock, push button, and other straightforward combinatorial logic. |
| S09-07-095270 | Structured Text should be used when calling AOIs, parameterised functions, and for iterative and/or complex logic. |
| S09-07-095280 | Function Block Diagram should be considered for analog signal processing, ramp-soak profiles, and closed-loop control (PIDs). |

Ladder: best for interlocks, motor control, pushbuttons, simple state machines; online status
visibility is its main advantage. Use looping/flow-control constructs only after careful
consideration. ST: no pointers, limited addressing, no recursion; good for configuration management,
AOI calls, generated code; harder to debug online. FBD: signal chains, PID. SFC: not covered
(unlikely in ALS-U subsystems).

In LogixForge terms: interlock groups and permissive latching in `.rll`; AOI-heavy routines
(DIAG_, marshalling, PermLatch calls in bulk) may be `.st`; FBD routines are passed through as XML.
