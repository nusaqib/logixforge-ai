# Coding standards (Logix 5000)

## Structure
1. Program per functional area; `MainRoutine` contains only JSRs (and first-scan init).
2. Scan order inside a program: inputs -> mode -> sequences/devices -> alarms -> outputs -> sim.
3. Routines 20-60 rungs; split by device group when larger.
4. Physical I/O referenced only in `R_Inputs` / `R_Outputs` (and module fault checks in `P_Utilities`).
5. Repeated devices are AOIs; repeated data are UDTs; HMI binds to one controller-scope UDT tag per device.

## Logic
6. One writer per tag. Never two OTEs on the same bit; never OTE plus ST assignment.
7. Stop has priority over start. Seal-in with NC stop wired healthy=1.
8. Every actuator output is gated by the safety status and permissives in `R_Outputs`.
9. Latches (OTL/OTU) only for faults and HMI momentary bit clearing; each OTL has one OTU; comment why.
10. One-shot storage bits are unique per use.
11. Timers: preset from `Cfg_` tags (ms), never magic numbers; retentive timers have a RES.
12. State machines: DINT `Step`, unique step numbers, timeout per step, abort state 900+, reset to 0
    path, `Step_Last` for edge detection. No JMP/MCR/AFI in production logic.
13. Faults latch, reset only when the cause is cleared and a reset is commanded.
14. HMI momentary commands cleared by the PLC when consumed.
15. ST for math/arrays/strings/algorithms; ladder for interlocks and sequencing visible to maintenance.
16. Division guarded; array indexes bounded; loops bounded and never on I/O.
17. Sim mode isolated: `Sim_Mode` alarm, outputs blocked, `R_Sim` last in scan.
18. First scan (`S:FS`) initialises step tags, clears commands, sets defaults if zero.

## Documentation
19. Description on every tag, member, parameter, module, program, routine (`//!`), task.
20. Rung comments explain intent ("Stop request: local, HMI, or E-stop"), not contacts.
21. `docs/SPEC.md` is kept in sync; `docs/CHANGELOG.md` per release; AOI `revision_note` per revision.

## Delivery
22. `lf validate` clean of errors; warnings justified.
23. Verify in Studio 5000 (Logic > Verify Controller) and run in Emulate before download.
24. Version control the spec; tag releases with the L5X hash and controller serial.
