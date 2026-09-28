---
name: plc-programs-tasks
description: Milestone 5 - define Logix programs (program.json), routine structure, and tasks (tasks.json: continuous, periodic, event) with priorities and watchdogs; scan-time budgeting and program parameters. Use when structuring a Studio 5000 project or adding a program/task.
---

# Programs and tasks

## `programs/<P_Name>/program.json`
```json
{ "name": "P_Conveyor", "main_routine": "MainRoutine", "fault_routine": "R_Fault",
  "description": "Conveyor line control", "disabled": false, "kind": "Normal" }
```
`kind: "Safety"` only inside the safety task (see `plc-safety`). Routines are discovered from
`routines/*.rll|*.st`. `main_routine` must exist. `fault_routine` (optional) runs on a major fault
in this program; use it to clear recoverable faults and log `S:MAJOR` info via `GSV(Program,THIS,MajorFaultRecord,...)`.

## `tasks.json`
```json
[
  { "name": "MainTask", "kind": "CONTINUOUS", "priority": 10, "watchdog_ms": 500,
    "programs": ["P_Utilities", "P_Conveyor", "P_Alarms", "P_Comms"], "description": "Main logic" },
  { "name": "T_Fast_10ms", "kind": "PERIODIC", "rate_ms": 10, "priority": 5, "watchdog_ms": 10,
    "programs": ["P_Counting"], "description": "High-speed inputs" },
  { "name": "T_PID_100ms", "kind": "PERIODIC", "rate_ms": 100, "priority": 7, "watchdog_ms": 100,
    "programs": ["P_Loops"], "description": "Process loops" },
  { "name": "T_Event", "kind": "EVENT", "event_trigger": "Module Input Data State Change",
    "event_tag": "Local:4:I", "priority": 3, "watchdog_ms": 5, "programs": ["P_Capture"] }
]
```
Rules: exactly one CONTINUOUS task (or none if everything is periodic); a program is scheduled in one
task only; priority 1 (highest) to 15; lower period gets higher priority; watchdog >= expected scan
time with margin; `programs` order = execution order inside the task.

## Architecture guidance
- Continuous task for general sequencing; keep it under ~30 ms typical on L8x. Use `GSV(Task,THIS,MaxScanTime,...)`
  in `P_Utilities` to expose scan time to the HMI.
- Periodic tasks for PID (100-500 ms), analog scaling, motion planning; keep them short. Total periodic
  load should stay below ~50 % so the continuous task still runs.
- Event tasks for high-speed capture only.
- I/O updates asynchronously to tasks. For consistent snapshots use `CPS` to copy input data at the
  start of `R_Inputs`; use `IOT` to force an output update in fast tasks.
- Program order inside a task: utilities/inputs first, control in the middle, alarms and outputs last.
- Program parameters (`usage` Input/Output/InOut/Public on program tags, v24+) let you reuse a
  program for identical equipment; otherwise use AOIs.

## Routine structure per program
`MainRoutine` (JSRs only), `R_Inputs`, `R_Mode`, `R_Seq_<Name>`, `R_Dev_<Name>`, `R_Alarms`,
`R_Outputs`, optional `R_Sim`, `R_Fault`. Validator warns `ROUTINE_UNCALLED` for routines without a JSR.

## Done when
`lf validate`: no `NO_TASKS`, `MULTI_CONT`, `TASK_PROG`, `PROG_MULTI_TASK`, `MAIN_ROUTINE`, `UNSCHEDULED`.
Scan-time budget documented in `docs/SPEC.md`.
