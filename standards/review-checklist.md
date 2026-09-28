# Review checklist and validator codes

## Validator codes (`lf validate`)
| Code | Level | Meaning / fix |
|---|---|---|
| NAME_CHARS / NAME_LEN / NAME_DBL_US / NAME_TRAIL_US | error | Logix name rules |
| NAME_RESERVED | error | Name is an instruction mnemonic or ST keyword |
| NAME_STYLE | warning | Does not match `naming.json` pattern |
| DUP_UDT / DUP_MEMBER / DUP_TAG / DUP_PROGRAM / DUP_PARAM | error | Duplicate in scope |
| UNKNOWN_TYPE | error | Data type not atomic/predefined/UDT/AOI |
| UDT_EMPTY / UDT_RECURSIVE / BOOL_ARRAY_UDT / BOOL_ARRAY | error | UDT/array layout rules |
| AOI_NO_LOGIC / AOI_USAGE / AOI_PARAM_TYPE / AOI_OPERANDS | error | AOI definition/call rules |
| TAG_NO_TYPE | error | Base tag without type |
| DESC_LEN | error (controller) / warning | Description longer than 128 characters; Studio 5000 rejects it on import |
| ALIAS_TARGET | warning | Alias target not found (add module XML) |
| MAIN_ROUTINE / FAULT_ROUTINE / JSR_TARGET | error | Routine reference missing |
| RUNG_SYNTAX / UNKNOWN_INSTR / OPERAND_COUNT | error | Rung text problems |
| UNDEF_TAG | warning (error in AOI) | Operand not defined in scope |
| ST_BLOCK / ST_TIMER | error | ST block imbalance / ladder timer in ST |
| ST_ASSIGN | warning | `=` where `:=` intended |
| NO_TASKS / MULTI_CONT / TASK_TYPE / TASK_RATE / TASK_PRIO / TASK_PROG / PROG_MULTI_TASK | error | Task rules |
| TAGALARM_UNSUPPORTED / DUP_ALARM / ALARM_TAG / ALARM_MEMBER / ALARM_COND / ALARM_SEV | error | Tag-based alarm rules (`plc-alarms`) |
| ALARM_MSG / ALARM_DELAY | warning | Alarm message missing / delay not a multiple of 500 ms |
| HMI_NO_SCREENS / HMI_HOME / HMI_CTRLREF / HMI_NAME / HMI_DUP / HMI_WIDGET / HMI_NAV / HMI_TAG / HMI_MEMBER / HMI_TYPE / HMI_CONST / HMI_ACCESS / HMI_FACEPLATE | error | `hmi/hmi.json` rules (`hmi-view-designer`) |
| HMI_SCOPE | warning | HMI bound to a program-scope tag |
| TASK_WD / UNSCHEDULED / ROUTINE_UNCALLED / EMPTY_ROUTINE / EMPTY_RUNG / FLOW_CTRL | warning | Structure quality |
| LATCH / NO_RUNG_COMMENT / NO_DESC / UDT_LAYOUT | info | Documentation/quality |

## Manual review checklist
### Safety and outputs
- [ ] Every physical output written in exactly one rung, in `R_Outputs`, gated by safety + permissives
- [ ] No standard logic writes safety tags; `Sim_` never touches safety
- [ ] E-stop / stop has priority; restart requires a new start command (no auto-restart after E-stop)
- [ ] Forces not present in L5X (`<Force`), `AFI` absent, `Sim_Mode` alarmed
### Correctness
- [ ] One writer per tag (OTE/OTL/OTU/MOV/ST) across all routines and programs
- [ ] ONS storage bits unique; timers have PRE from config; RTO/CTU have RES; TOF semantics intended
- [ ] State machines: every state has an exit, a timeout, and an abort path; step reset on first scan
- [ ] Faults latch and reset only when cleared; alarms have ack; HMI momentary bits cleared
- [ ] Math: divisions guarded, REAL/DINT conversion intended, array indexes bounded
- [ ] Comms: MSG/produced-consumed have timeout/heartbeat handling
### Structure and standards
- [ ] MainRoutine only JSRs; routines called; scan order inputs -> logic -> alarms -> outputs
- [ ] Program scope by default; controller scope justified; names per `naming.json`
- [ ] Descriptions and rung comments present; SPEC.md matches behaviour
- [ ] Task periods/priorities/watchdogs sensible; periodic load < 50 %
### Delivery
- [ ] `lf validate` clean; L5X built; Studio 5000 verify pending/done; Emulate test evidence
