---
name: plc-structured-text
description: Milestone 7 - write Logix Structured Text (ST) routines as .st files for LogixForge. Covers Logix ST syntax and differences from IEC 61131-3, timers/counters in ST, CASE state machines, loops, strings, and when to prefer ST over ladder. Use for ST authoring or editing in Studio 5000 projects.
---

# Structured Text routines (.st)

## File format `programs/<P>/routines/<R_Name>.st`
Plain Logix ST. First line `//! description` optional. Comments `//` or `(* *)`. Each line becomes an
`STContent/Line` in L5X, so keep lines <= 120 chars.

## Logix ST essentials (differs from other IEC vendors)
- Assignment `:=`; equality `=`; not-equal `<>`; comparison result is BOOL; no `==`.
- Non-retentive assignment `[:=]` (output cleared when the routine/AOI is not scanned).
- Keywords: `IF ... THEN ... ELSIF ... ELSE ... END_IF;` `CASE x OF 1: ... 2,3: ... 10..20: ... ELSE ... END_CASE;`
  `FOR i := 0 TO 9 BY 1 DO ... END_FOR;` `WHILE ... DO ... END_WHILE;` `REPEAT ... UNTIL ... END_REPEAT;` `EXIT;`
- Booleans: `AND OR XOR NOT`, bit access `Word.5`, `Word.[i]` (indexed bit), arrays `A[i]`, `A[i,j]`.
- Numeric: `+ - * / MOD **`, functions `ABS SQRT LN LOG SIN COS TAN ASIN ACOS ATAN DEG RAD TRUNC`.
- **No TON/TOF/CTU in ST.** Use the function-block versions with `FBD_TIMER` / `FBD_COUNTER` tags:
  ```
  T_Delay.PRE := Cfg_Delay_ms;
  T_Delay.TimerEnable := Run AND NOT Feedback;
  TONR(T_Delay);
  Fault := T_Delay.DN;
  ```
  Same for `TOFR`, `RTOR`, `CTUD`. Reset via `T_Delay.Reset := 1;` for one scan.
- Instructions callable as procedures: `MOV`, `COP(Src,Dst,Len)`, `CPS`, `FLL`, `SIZE`, `JSR(Routine)`,
  `GSV(ClassName,InstanceName,AttributeName,Dest)`, `SSV`, `OSRI/OSFI(OneShot)` with `FBD_ONESHOT`,
  `PIDE(Loop)`, `MSG(Msg)`, string instructions `CONCAT(a,b,dst)` `MID` `FIND` `DTOS` `STOD`.
- Strings: `S := 'text';` `S.LEN`, `S.DATA[0]`; `$'` escapes a quote, `$N` newline, `$$` dollar.
- Integer division truncates; mixed REAL/DINT promotes to REAL; assignment to DINT rounds (not truncates).
- No local variables. Every identifier is a program/controller tag. Loop indices are tags.
- Loops run to completion in one scan; guard with a bound and never `WHILE` on I/O.

## When to use ST
Math and scaling, arrays and recipes, string handling, comms parsing, state machines with many
transitions, algorithms (ramping, totalising). Keep discrete interlocks in ladder for maintainers.

## Patterns
**State machine:**
```
CASE Step OF
    0:  IF Cmd_Start AND Permissive THEN Step := 10; END_IF;
    10: Cmd_ValveOpen := 1;
        IF Sts_ValveOpened THEN Step := 20;
        ELSIF T_Step.DN THEN Step := 900; END_IF;
    900: Cmd_ValveOpen := 0;   // abort
        IF Cmd_Reset THEN Step := 0; END_IF;
ELSE
    Step := 0;
END_CASE;
T_Step.TimerEnable := (Step <> Step_Last);   // restart timer on step change
```
**Scaling:** `EU := (Raw - Cfg_RawMin) * (Cfg_EUMax - Cfg_EUMin) / (Cfg_RawMax - Cfg_RawMin) + Cfg_EUMin;`
guard the divisor: `IF (Cfg_RawMax - Cfg_RawMin) <> 0 THEN ... END_IF;`
**Array loop:** `FOR i := 0 TO 15 DO Alm_Any := Alm_Any OR Alm_Bits.[i]; END_FOR;`

## Validator checks
`ST_BLOCK` (unbalanced IF/CASE/FOR/...), `ST_ASSIGN` ('=' where ':=' likely), `ST_TIMER` (TON in ST).
Logix compiles ST only in Studio 5000; keep statements simple and test in Emulate.
