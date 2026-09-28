---
name: alsu-hmi
description: ALS-U site profile for Studio 5000 View Designer HMIs (PanelView 5510) - screen hierarchy, palette, fonts, LED and UDT faceplate conventions, security roles and interaction patterns derived from the ALS-U reference HMI, applied on top of the generic hmi-view-designer skill. Use for any HMI/PanelView/View Designer task on an ALS-U system.
---

# ALS-U HMI profile

Profile root: `${CLAUDE_PLUGIN_ROOT}/profiles/alsu/`. Conventions: `standards/hmi.md` (derived from the
reference export `examples/masterCode/hmi-export/`, PanelView 5510 2715P-T15CD, View Designer v9).
Alarms are EPICS's job (`standards/epics.md`); the PanelView is a local engineering panel.

## Procedure
1. Load `hmi-view-designer` (format, widgets, import) and read `standards/hmi.md`.
2. Start `hmi/hmi.json` with the ALS-U defaults:
   ```json
   { "controller_ref": "<CPU name>", "terminal": { "catalog": "2715P-T15CD" }, "banner": false,
     "controller": { "cip_path": "<path from the HMI>", "acd_path": "<ACD path>" },
     "style": { "lamp_shape": "ellipse", "font_size": 14,
                "colors": { "on": "#51e79a", "fault": "#ff0000", "accent": "#00baff", "button": "#263a4e", "panel": "#e7e8e9" } },
     "folder_security": { "Configuration": { "Operator": "ReadOnly", "Engineer": "FullAccess" },
                          "Calibration":   { "Operator": "ReadOnly", "Engineer": "FullAccess" } },
     "home_screen": "HOME", "screens": [ ... ] }
   ```
3. Screen set: `HOME`, `Menus/Menu_Main` (+ Details/Configuration/Calibration menus), `Details/<Device>`
   per device group, `Configuration/<System>`, `Calibration/<System>`, `External_Subsystems/<MPS|PPS|Vacuum>`.
   Every screen gets a `nav_button` back to HOME and to its menu.
4. Faceplates: one per device UDT, rows `_Val` numeric (units from the tag's `@EngineeringUnit` where the
   generic rule needs units), `_Sts`/`_Wrn`/`_Ltch`/`_FF` indicators (green OK, red fault), `_Byp` toggle,
   `_SP`/`_H_SP`/`_L_SP` numeric inputs with keypad limits; `_Rst` buttons are `momentary`.
5. Reuse the reference AOGs by name where a generated faceplate would duplicate them (`LED_Fault_Circle`,
   `UDT_ai`, `UDT_bi`, `UDT_RF_Power`); copy their `.hmi` files from the export into the package's
   `Assets/Add-On Graphics/` when the target project does not already contain them.
6. `lf validate` then `lf hmi build`; report which conventions were applied and what remains manual
   (custom top bar, PDF documents, trends, editing-mode gating - see `standards/hmi.md`).
