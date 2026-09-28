---
name: plc-udts
description: Milestone 1 - design and write Logix User-Defined Data Types (UDTs) as datatypes/*.json for LogixForge. Use when creating or changing structures for equipment interfaces, HMI, recipes, alarms, or comms in a Studio 5000 project.
---

# User-Defined Data Types

## File format `datatypes/<UDT_Name>.json`
```json
{
  "name": "UDT_Valve",
  "description": "Two-position valve HMI/logic interface",
  "members": [
    { "name": "Cmd_Open",  "data_type": "BOOL", "description": "HMI open command (momentary)" },
    { "name": "Cmd_Close", "data_type": "BOOL", "description": "HMI close command (momentary)" },
    { "name": "Sts_Opened","data_type": "BOOL", "description": "Open limit switch made" },
    { "name": "Sts_Closed","data_type": "BOOL", "description": "Closed limit switch made" },
    { "name": "Sts_Fault", "data_type": "BOOL", "description": "Travel timeout fault" },
    { "name": "Cfg_TravelTime_ms", "data_type": "DINT", "description": "Max travel time" },
    { "name": "Sts_Position", "data_type": "REAL", "description": "Position feedback 0-100 %" },
    { "name": "Alarms", "data_type": "UDT_AlarmBits", "description": "Nested alarm structure" },
    { "name": "Log", "data_type": "DINT", "dimension": 10, "description": "Last 10 events" }
  ]
}
```
Optional per member: `"radix"` (Decimal/Hex/Binary/Float/ASCII), `"external_access"` (Read/Write, Read Only, None).
String UDTs: `"family": "StringFamily"` with members `LEN` (DINT) and `DATA` (SINT, dimension N, radix ASCII).

## Rules (Logix hard limits)
- Name <=40 chars, no reserved words (instruction mnemonics, ST keywords), unique case-insensitively.
- Member types: atomic (BOOL, SINT, INT, DINT, LINT, REAL, LREAL, USINT/UINT/UDINT/ULINT on v32+),
  predefined (TIMER, COUNTER, STRING, ...), other UDTs (no recursion), AOI types are NOT allowed.
- BOOL arrays inside a UDT must be dimensioned in multiples of 32 (prefer a DINT bit-field member).
- Max 512 members (nesting counts), max 2 MB per tag.
- UDT changes that alter layout force a download; design members up front, leave `Spare` DINTs
  for future growth in production systems.

## Design rules (house standard)
- Prefix `UDT_`. Group members by prefix and order: `Cmd_` (HMI/PLC commands), `Cfg_` (config/setpoints),
  `Sts_` (status), `Alm_` (alarms), `Sim_` (simulation), then internals (`_` prefix not allowed;
  use `Int_`).
- Pack BOOLs together: Logix packs consecutive BOOLs into one DINT (up to 32); interleaving
  BOOL/DINT wastes 4 bytes each. Put BOOLs first, then SINT/INT, then DINT/REAL, then structures.
- One UDT per device class for HMI (motor, valve, analog input, PID loop) so faceplates bind
  to a single tag.
- Descriptions on every member. HMI and alarm systems import them.
- Do not put I/O references or aliases inside UDTs; map in routines.
- Version the UDT in its description (`v1.2 2026-09-28: added Sts_Position`).

## Checklist before moving on
- `python -m logixforge.cli validate <project>` shows no `UNKNOWN_TYPE`, `DUP_MEMBER`, `BOOL_ARRAY_UDT`.
- Dependency order does not matter in the spec (the writer emits all DataTypes; Studio 5000
  resolves order on import), but a UDT used by an AOI parameter must exist.
- Record a partial import file if the customer will pull the UDT into an existing project:
  `python -m logixforge.cli partial <project> --kind DataType --name UDT_Valve`.
