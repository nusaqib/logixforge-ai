---
name: plc-alarms
description: Define controller alarms for a Studio 5000 project - tag-based alarm conditions (alarms.json, Logix v31+ on 5x80 controllers, shown natively by PanelView 5000 / FactoryTalk Alarms & Events) and the ALMD/ALMA instruction alternative for older controllers. Use when adding alarms, alarm messages, severities, or alarm handling logic.
---

# Alarms

PanelView 5000 and FactoryTalk Alarms & Events read alarms **from the controller**. Define them once in
the PLC spec; the HMI only displays them.

## Tag-based alarms (preferred, v31+ ControlLogix 5580 / CompactLogix 5380/5480)
`alarms.json` in the project root:
```json
[
  { "name": "Conveyor01_Fault", "input": "Alarms.Conveyor01_Fault",
    "message": "Conveyor 01: run feedback missing (check contactor)", "severity": 750,
    "class": "Conveyor", "hmi_group": "Line", "on_delay_ms": 0, "latched": false, "ack_required": true },
  { "name": "Tank_LevelHigh", "input": "HMI_Tank.Sts_Level_pct", "condition": "HI", "limit": 90.0,
    "deadband": 2.0, "message": "Tank level high", "severity": 600, "class": "Process" }
]
```
- `input`: `<controller tag>[.member...]`. Put alarm bits in one controller-scope UDT tag (`Alarms : UDT_Alarms`)
  written from `R_Alarms`; analog alarms attach to the `Sts_` member of the device UDT.
  Program-scope tags work (`"program": "P_X"`) but are harder to browse from the HMI.
- `condition`: BOOL -> `TRIP` (default). Numeric -> `HI HIHI LO LOLO ROC_POS ROC_NEG DEV_HI DEV_LO` with
  `limit` (and `target_tag` for DEV_*).
- `severity` 1..1000 (1000 most severe). House scale: 1000 safety, 750 equipment fault, 500 process,
  300 warning/information. `class` groups for filtering; `hmi_group` for the HMI.
- `on_delay_ms`/`off_delay_ms` in multiples of 500 (evaluation period). `latched` requires an operator
  reset after the condition clears. `ack_required` false for information-only.
- Messages: sentence, device first, then cause and action, <= 80 chars for PanelView rows.
- Generated into L5X as `<AlarmConditions>` on the tag (Logix Import/Export RM014 ch. 7). Validator codes:
  `TAGALARM_UNSUPPORTED`, `ALARM_TAG`, `ALARM_MEMBER`, `ALARM_COND`, `ALARM_SEV`, `ALARM_MSG`, `ALARM_DELAY`.
- Limitation: alarm definitions on AOI/UDT *definitions* (auto-instantiated) are not generated yet; list
  instances explicitly.

## Instruction-based alarms (ALMD/ALMA, any controller v16+)
Use when the controller is L7x/CompactLogix 5370 or the customer standard requires ALMD:
- Tag `ALM_<Name> : ALARM_DIGITAL` (message/severity configured in the tag's alarm properties in Studio 5000,
  or `<Data Format="Alarm">` in L5X).
- Rung: `XIC(Alarms.Conveyor01_Fault)ALMD(ALM_Conveyor01_Fault,Alarms.Conveyor01_Fault,0,0,0,0);`
  (operands: alarm tag, In, ProgAck, ProgReset, ProgDisable, ProgEnable). `ALMA` for analog.
- Keep them in `R_Alarms`; one rung per alarm; document message text in the rung comment until the
  writer supports `Data Format="Alarm"` (roadmap).

## Alarm logic pattern (both kinds)
1. Detect in the device/AOI (`Fault` output), 2. copy to `Alarms.<bit>` in `R_Alarms`, 3. summary `Alarm_Any`
for the banner, 4. `Sys_AlarmAck` from HMI clears/acks (PLC clears the ack bit), 5. faults reset only when
the cause is gone. No alarm text in ladder comments; it lives in `alarms.json`.
