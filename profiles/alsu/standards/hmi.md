# ALS-U HMI conventions (derived from the masterHMI View Designer export, 2025)

AL-1605-0840 does not cover HMI design. These conventions are extracted from the ALS-U reference HMI
(`examples/masterCode/hmi-export`, PanelView 5510 2715P-T15CD, 1024x768, View Designer v9) and are
the defaults for `alsu-hmi` until an ALS-U HMI standard document exists. Operator alarms live in
EPICS (epics.md); the PanelView is a local engineering/maintenance panel.

## Project structure
- Controller reference named after the ACD (`masterCode`); bindings `::masterCode.<Tag>`.
- Home screen `HOME`; navigation shortcuts `HOME` and `Settings` only. Everything else is reached
  through menu screens and on-screen buttons (43 buttons navigate back to HOME).
- Screen folders (User-Defined Screens): `Menus/` (Menu_Main, Menu_Details, Menu_Configuration,
  Menu_Calibration), `Details/` (one per device group: Cavity, Tuner1/2, RF_Power, Arc_Detectors,
  HP_RF_Chain, HP_Coax_Switch, LLRF1/2_Analog, TCU, Cavity_LCW, Cavity_Temp, Auxilliary),
  `Configuration/` and `Calibration/` (setpoints, calibration, per system), `External_Subsystems/`
  (MPS, PPS, Vacuum), `Trends/`, `Documents/` (PDF manual via PDF_Viewer AOG).
- Security: Configuration and Calibration screens carry `SecurityRoles { Operator := ReadOnly; Engineer := FullAccess }`.
- Editing on configuration screens is gated by a PLC "editing mode" tag (`RF_Power_Editing_Mode`)
  set/cleared by buttons; inputs are `NumericInput` with `KeypadMinValue/KeypadMaxValue`.

## Screen layout (1024x768)
- `ShowDefaultBanner := false`; every screen draws its own top bar: navigation back/forward/menu
  groups and logon group at top-left (Y 8, 32 px high), date/time and controller/network status
  indicators at top-right, screen title centred (`TextDisplay`, size 18, X ~402, W ~219).
- Content starts at Y ~137; device panels are `Rectangle` groups (~228 x 493) with a title label above.
- Buttons 98.5 x 45; Home button bottom-left, action/navigation buttons bottom-right column.
- Background white `#ffffff`; panels `#e7e8e9` / `#e5e5e5`; dark `#1e2e3e` for headers and borders.

## Palette (as used)
| Meaning | Colour |
|---|---|
| Buttons / navigation | `#263a4e` (text white) |
| Accent, bar level, active selection | `#00baff` |
| OK / enabled / permit | `#51e79a` |
| Fault / trip / latched | `#ff0000` |
| Inactive lamp | `linear-gradient(to bottom, #d1d3d4 0.00%, #939598 100.00%)` or `#bcbec0` |
| Dark green (secondary OK) | `#315802` |

## Typography
`Arial Unicode MS`; 14 body labels, 15 bold values, 12 small labels, 13 secondary, 18 titles, 8.3 in the top bar.

## Reusable graphics (Add-On Graphics)
- LEDs: `LED_Fault_Circle` (15x15 Ellipse, red `#ff0000` when 0, green `#51e79a` when 1), `LED_Fault_Square`,
  `LED_Status`, `LED_Status_Inverse`; one untyped user property `^Tag` bound with `Expression := "" -> "Tag"`.
- UDT faceplates, named after the UDT with a user property of the same name typed `::masterCode.<UDT>`:
  `UDT_ai` (153x22: value `UDT_ai.Val` with units from the tag's extended property `UDT_ai.@EngineeringUnit`,
  status/warning/latch LEDs; expression bindings such as `UDT_ai.Ltch+(UDT_ai.Ltch*UDT_ai.Byp)`),
  `UDT_ai_Config`, `UDT_ai_Calib`, `UDT_bi`, `UDT_RF_Power` (+ `_Config`, `_Calib`), `UDT_ArcDet` (+ `_Config`),
  `LLRF_Analog`, `Numeric_Display`, `PDF_Viewer_Landscape/Portrait`.
- Instantiation: `UDT_ai UDT_ai_001 ( UDT_ai := "::masterCode.Feeder1.Circ_LCWR_Flow" ) { X..Access }`.

## Interaction
- Momentary commands (reset, strobe): `BehaviorSetTagTo1OnPress0OnRelease` with `^Tag`, `minimumHoldTime := 0`.
- Latched commands / mode selection: `BehaviorSetTagTo1OnRelease`, `BehaviorSetTagTo0OnRelease`,
  `BehaviorToggleTagOnRelease`; `CheckBox` / `RadioButton` bound to bit members with `StateTable` on `ShowMark`.
- Colour animation: `ColorStateTable` (`fillcolor`) on Ellipse/Rectangle/Button; text animation: `StateTable` (`Text`).
- Bar graphs: `BarGraph` with `LevelColor`, `MinValue`, `MaxValue`.

## LogixForge mapping (`alsu-hmi`)
`hmi.json` defaults for ALS-U: `"terminal": {"catalog": "2715P-T15CD"}`, `"banner": false`,
`"style": {"lamp_shape": "ellipse", "font_size": 14, "colors": {"on": "#51e79a", "fault": "#ff0000",
"accent": "#00baff", "button": "#263a4e", "panel": "#e7e8e9"}}`, folders `Details/Configuration/Calibration`
with `folder_security` for Configuration and Calibration, `momentary` buttons for `_Rst`, faceplates
per device UDT (rows: `_Val` numeric, `_Sts`/`_Wrn`/`_Ltch` indicators, `_Byp` toggle, `_SP` inputs).
Not generated yet: the custom top bar (screens keep the system banner off and a plain title), PDF
documents, trends, editing-mode gating.
