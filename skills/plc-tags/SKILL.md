---
name: plc-tags
description: Milestone 3 - define controller-scope and program-scope tags, aliases to I/O, initial values, produced/consumed tags and program parameters for a Studio 5000 project (tags/*.json, programs/*/tags.json). Use when adding, renaming or scoping tags.
---

# Tags

## Formats
Controller scope: any `tags/*.json` (list). Program scope: `programs/<P>/tags.json`.
```json
[
  { "name": "HMI_Conveyor01", "data_type": "UDT_Motor", "description": "HMI interface conveyor 01",
    "value": { "Cmd_Start": 0, "Cfg_FaultDelay_ms": 2000 } },
  { "name": "I_PB_Start", "alias_for": "Local:2:I.Data.0", "description": "Start PB, NO" },
  { "name": "Recipe", "data_type": "UDT_Recipe", "dimensions": "20", "description": "Recipe table" },
  { "name": "Cfg_LineSpeed", "data_type": "REAL", "value": 1.5, "constant": true, "description": "m/s" },
  { "name": "PC_LineStatus", "data_type": "UDT_LineStatus", "produced": { "count": 1 }, "description": "To line PLC" },
  { "name": "PC_UpstreamStatus", "data_type": "UDT_LineStatus",
    "consumed": { "producer": "Upstream_PLC", "remote_tag": "PC_LineStatus", "rpi": 20 }, "description": "From upstream PLC" },
  { "name": "Motor_Cmd", "data_type": "BOOL", "usage": "Input", "description": "Program parameter (v24+)" }
]
```
- `value` is optional; structures use member-order dict or a list; arrays use lists. Omitted = 0.
- `external_access`: `Read/Write` (default), `Read Only`, `None` (hide from HMI/comms).
- `radix`: Decimal (default), Float for REAL, Hex/Binary/ASCII when helpful for maintenance.

## Scoping rules
- **Program scope by default.** Controller scope only for: HMI interface UDTs (one tag per device),
  produced/consumed, data shared across programs, MSG buffers, system diagnostics.
- Alias tags for physical I/O live at controller scope in `tags/io.json`, prefix `I_` / `O_`,
  `AI_` / `AO_`. Aliases only to I/O; never alias a tag to another program tag (harder to trace).
- Program tags with the same name in two programs are legal but confusing; the validator warns.
- AOI instance tags (`data_type` = AOI name) belong where the AOI is called.

## Naming (see `standards/naming-conventions.md`)
- PascalCase_With_Underscores between words; units suffix for engineering values (`_ms`, `_degC`, `_pct`).
- Prefixes: `I_ O_ AI_ AO_` physical, `HMI_` HMI interface, `Cfg_` config, `Sts_` status, `Alm_` alarm,
  `T_` TIMER, `C_` COUNTER, `ONS_` one-shot storage, `PC_` produced/consumed, `Sim_` simulation.
- No spaces, no leading digit, <=40 chars, not an instruction mnemonic (validator: `NAME_RESERVED`).

## Initial values and retentivity
- Everything in Logix is retentive across power cycles (battery/ESM) but NOT across downloads.
  Setpoints the operator changes at runtime should be documented; consider a recipe/HMI store.
- `constant: true` protects engineering constants from HMI/online edits.
- For safety programs, tags are restricted; see `plc-safety`.

## I/O aliases need modules
`Local:2:I.Data.0` only exists if slot 2 has a module in `modules/`. Until the module XML is added,
keep the tag as a base BOOL with a `TODO alias_for` in the description (validator warns `ALIAS_TARGET`).

## Done when
`lf validate` shows no `DUP_TAG`, `UNKNOWN_TYPE`, `TAG_NO_TYPE`; every tag has a description; the I/O
list in `docs/SPEC.md` matches `tags/io.json` one-to-one.
