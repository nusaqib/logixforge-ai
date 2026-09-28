---
name: hmi-view-designer
description: Milestone 13 - generate a Studio 5000 View Designer (PanelView 5000) HMI from the PLC spec - hmi/hmi.json screens and widgets, Add-On Graphic faceplates derived from UDTs, navigation shortcuts, controller-bound tags, and the import procedure. Use whenever the user mentions HMI, PanelView 5000, View Designer, faceplates, screens, or operator interface for a Logix project.
---

# HMI for Studio 5000 View Designer (PanelView 5000)

View Designer binds screens **directly to the Logix project** (controller reference -> .ACD) and shows
the **controller's own alarms**. So the HMI milestone has two halves:
1. PLC side: controller-scope `HMI_*` UDT tags (done in `plc-tags`) and tag-based alarms (`plc-alarms`).
2. HMI side: `hmi/hmi.json` -> `lf hmi build` -> import folder of text `.hmi` files (View Designer v9+).

## Spec `hmi/hmi.json`
```json
{ "target": "view-designer", "project_name": "Line_HMI", "controller_ref": "LGX",
  "terminal": { "catalog": "2715P-T10CD" },            // 7WD/9WD 800x480, 10CD/12WD 1280x800, 15CD 1024x768, 19CD 1280x1024
  "home_screen": "Overview",
  "screens": [
    { "name": "Overview", "title": "Line overview", "columns": 3, "widgets": [
      { "type": "faceplate",     "tag": "HMI_Conveyor01", "label": "Conveyor 01" },
      { "type": "indicator",     "tag": "I_ESTOP_OK", "label": "E-Stop", "on_text": "OK", "off_text": "E-STOP", "on_color": "#2ecc71", "off_color": "#e74c3c" },
      { "type": "numeric",       "tag": "HMI_Tank.Sts_Level_pct", "label": "Level", "units": "%", "decimals": 1 },
      { "type": "numeric_input", "tag": "HMI_Tank.Cfg_SP_pct", "label": "Setpoint", "units": "%", "min": 0, "max": 100 },
      { "type": "bargraph",      "tag": "HMI_Tank.Sts_Level_pct", "label": "Level", "min": 0, "max": 100 },
      { "type": "button",        "text": "Ack all", "tag": "Sys_AlarmAck", "action": "set1" },     // set1 | set0 | toggle
      { "type": "nav_button",    "text": "Alarms", "screen": "Navigation Menu\\AlarmSummary" },    // or another screen name
      { "type": "text",          "text": "Free text", "span": 2 } ] } ],
  "faceplates": { "UDT_Motor": { "title": "Motor", "rows": [ { "type": "indicator", "member": "Sts_Run", "label": "Running" } ] } }
}
```
- Widgets flow into a grid (`columns`), left to right; `span` widens a widget. Faceplates size themselves.
- **Faceplates** are Add-On Graphics generated per UDT. Rows derive automatically from member prefixes
  (`Cmd_` button, `Sts_`/`Sim_` BOOL indicator, `Alm_`/`*Fault*` red indicator, `Cfg_` numeric input,
  other numerics display). Override with `faceplates.<UDT>.rows` when the automatic layout is not right.
- Bindings are always controller scope: `::<controller_ref>.<Tag>`. Program-scope tags are rejected.
- Predefined targets for `nav_button.screen`: `Navigation Menu\AlarmSummary`, `Navigation Menu\AlarmManager`,
  `Navigation Menu\Settings`, `Predefined Screens\ControllersGeneral` (others per View Designer help).

## Build and import
```
python -m logixforge.cli validate <project>          # HMI_* findings: unknown tags, wrong types, constant tags, bad access
python -m logixforge.cli hmi build <project>         # -> <project>/build/hmi/<project_name>/...
python -m logixforge.cli hmi docs <project>          # -> docs/HMI_TAGS.md, docs/ALARMS.csv
```
`lf hmi build` writes one package `build/hmi/<name>/`. In View Designer: create the project for the
same terminal, add a **controller reference named as `controller_ref`** pointing at the .ACD built
from this spec, then **File > Import Project > `<name>/ViewApplication.hmi`**. One pass imports
screens, shortcuts and Add-On Graphics (verified on a fresh project). An import with any error is
discarded as a whole, so fix the log and re-import. Imported elements overwrite same-named ones (a
backup .vpd is created). Import scales screens if the terminal differs; better to generate for the
right terminal.

## Rules
- Every widget tag must be a controller-scope tag with `ExternalAccess` Read/Write (writes) or at least
  Read Only (displays). The validator enforces this (`HMI_TAG`, `HMI_ACCESS`, `HMI_CONST`, `HMI_TYPE`).
- One faceplate per device UDT; screens show faceplates, not loose device bits.
- Momentary commands: HMI sets `Cmd_` bits, the PLC clears them (the ladder patterns do this).
- Alarm display is not drawn by us: use the predefined Alarm Summary/Manager screens; alarm text,
  severity and class come from `alarms.json`.
- Keep screen names <= 40 chars, identifiers only; titles are free text.

## What has been verified vs. inferred
Element and property names come from Rockwell's 9324-RM001 examples, corrected by real import logs:
- Confirmed by import: Screen, Button, TextDisplay, NumericDisplay, NumericInput, Rectangle, StateTable
  (must have a unique name, never the keyword `StateTable` itself), BehaviorNavigateToScreen,
  BehaviorSetTagTo1OnRelease/…, AddOnGraphic + UserProperties, Shortcut, ViewProject.
- Rejected by import (never emit): `ForceAnimations` on elements or screens; `TagName` on button
  behaviors; `MinValue`/`MaxValue` on NumericInput (clamp setpoints in the PLC instead).
- Confirmed in later rounds: `^Tag` as the behavior's tag property, StateTable state properties
  `fillcolor`/`text`, UDT-typed AOG user property `::REF.UDT_x`, and `using ViewDesigner::AOG;` on
  screens (required to resolve user AOGs). An empty `HomeScreen := "";` is rejected; omit the line.
Reading an import log: "no viable alternative at input 'X'" is a syntax error at X; "Couldn't resolve
reference to Member 'X'" means X is not a property of that element; "Couldn't resolve reference to
HMIDefinition 'X'" means the element type X is unknown (or its Add-On Graphic file failed to parse).
Fix the constant or emitter, `lf hmi build`, re-import, and tell the user what changed.

## FactoryTalk View / Optix
Not generated yet; see `hmi-factorytalk` for the roadmap. The `hmi docs` output (tag interface and
alarm CSV) is the hand-off for those platforms in the meantime.
