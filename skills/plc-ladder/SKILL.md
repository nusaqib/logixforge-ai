---
name: plc-ladder
description: Milestone 6 - write Logix ladder (RLL) routines as .rll neutral-text files that LogixForge compiles to L5X. Covers rung text grammar, branches, timers/counters, one-shots, seal-ins, state machines, JSR structure, AOI calls, and the ladder patterns used in production Rockwell code. Use for any ladder logic authoring or editing.
---

# Ladder routines (.rll)

## File format `programs/<P>/routines/<R_Name>.rll`
```
//! One-line routine description (first line, optional)
// Rung comment (any number of lines directly above the rung)
XIC(PB_Start)XIO(PB_Stop)OTE(Run);

// Blank line separates rungs. A rung may wrap lines; it ends at ';'
[XIC(Start)ONS(ONS_Start),XIC(Run)]
XIO(Stop)XIO(Fault)OTE(Run);
```
Rung text is exactly Studio 5000's neutral text (what you see in Edit > Copy of a rung). Rules:
- Instruction call `MNEMONIC(op1,op2,...)`; no spaces needed; `?` lets Logix fill accumulators
  (`TON(T_1,?,?)`, `CTU(C_1,?,?)`).
- Parallel branch `[levelA,levelB,...]`; nest freely `[XIC(A)[XIC(B),XIC(C)],XIC(D)]`.
- Literals: `100`, `1.5`, `16#00FF`, `2#1010`, `'text'`. Bits: `Word.3`, `Local:2:I.Data.0`, `Tag[3].Member`.
- AOI call: `AOI_Motor(Instance,<required params in definition order>)`; non-required params are
  set through the instance tag (`MOV(x,Instance.Param)`).
- Status bits: `S:FS` first scan, `S:MINOR` minor fault; no `S:N`/`S:Z` on Logix 5000 (use CMP).
- Check any rung quickly: `python -m logixforge.cli rung check "XIC(A)OTE(B);"`.

## Structure of a program's ladder
- `MainRoutine`: only `JSR` calls in scan order, plus first-scan housekeeping. No logic.
- `R_Inputs`: raw I/O -> program tags, NC contact inversion, debounce, analog scaling.
- `R_<Function>`: one routine per function/device group. 20-60 rungs is a good size.
- `R_Alarms`: alarm bits, summary, ack handling.
- `R_Outputs`: program tags -> physical outputs, every rung gated by safety/permissive bits.
- Rung comments in the form "What / why", not a restatement of the contacts.

## Patterns (copy these)
**Seal-in start/stop (stop has priority, NC stop wired healthy=1):**
```
[XIC(PB_Start),XIC(Run)]XIC(PB_Stop_OK)XIO(Fault)OTE(Run);
```
**One-shot rising edge:** `XIC(Trigger)ONS(ONS_Trigger)OTE(Pulse);` (ONS storage bit per use, never reuse).
**On-delay:** `XIC(Cond)TON(T_Cond,?,?);` then use `T_Cond.DN`. Preset in ms via `T_Cond.PRE` from Cfg tags.
**Retentive timer + reset:** `XIC(Run)RTO(T_Run,?,?);` ... `XIC(Reset)RES(T_Run);`
**Free-running pulse:** `XIO(T_Pulse.DN)TON(T_Pulse,?,?);` toggles every PRE ms.
**Counter with reset:** `XIC(Sensor)ONS(ONS_Sensor)CTU(C_Parts,?,?);` `XIC(Reset)RES(C_Parts);`
**Compare / math:** `GRT(Level,Cfg_HighLevel)OTE(Alm_LevelHigh);` `CPT(Out,(In-Zero)*Span/Raw);`
**State machine (DINT step):**
```
// Step 0 -> 10 on start
EQU(Step,0)XIC(Cmd_Start)MOV(10,Step);
// Step 10: open valve, wait for opened or timeout
EQU(Step,10)OTE(Cmd_ValveOpen);
EQU(Step,10)TON(T_Step,?,?);
EQU(Step,10)XIC(Sts_ValveOpened)MOV(20,Step);
EQU(Step,10)XIC(T_Step.DN)MOV(900,Step);
```
Keep the step number unique per state, put the abort state at 900+, and reset `T_Step` on step change
(`NEQ(Step,Step_Last)RES(T_Step)` then `MOV(Step,Step_Last)`).
**Latches:** avoid `OTL/OTU` for process state; acceptable for faults and HMI momentary bit clearing.
Every `OTL` must have exactly one `OTU` and a comment on why it is retentive.
**Output mapping:** `XIC(Cmd_Run)XIC(Safety_OK)XIO(Sim_Mode)OTE(O_Motor);`

## Do not
- Drive one tag from two OTEs (last one wins, maintenance nightmare). Validator warns.
- Use `JMP/LBL` or `MCR` to skip logic; outputs inside keep stale state. Use step logic.
- Put `AFI` in production code; use a `Sim_` bit.
- Use `ONS` inside branches that are not always scanned.
- Reference raw I/O outside `R_Inputs`/`R_Outputs`.
- Use `TND` except in controlled fault handling.

## Done when
`lf validate` shows no `RUNG_SYNTAX`, `UNKNOWN_INSTR`, `OPERAND_COUNT`, `JSR_TARGET`, `UNDEF_TAG`
errors. Warnings on `FLOW_CTRL`, `LATCH` are reviewed and justified in the rung comment.
For instruction operand order see `${CLAUDE_PLUGIN_ROOT}/standards/instruction-reference.md`.
