---
name: alsu-hmi
description: ALS-U site profile for Studio 5000 View Designer HMIs - screen hierarchy, colour meanings, faceplate layouts per device class, navigation and security per the ALS-U HMI standard, applied on top of the generic hmi-view-designer skill. Use for any HMI/PanelView/View Designer task on an ALS-U system.
---

# ALS-U HMI profile

Profile root: `${CLAUDE_PLUGIN_ROOT}/profiles/alsu/`.

## Procedure
1. Load `hmi-view-designer` (format, widgets, import procedure) and `plc-alarms`.
2. Read `profiles/alsu/standards/hmi.md` and `alarms.md`; they override generic colours, layouts,
   severities and navigation rules.
3. Start `hmi/hmi.json` from `profiles/alsu/templates/hmi/` fragments and faceplate contracts; take
   screen structure from the reference export in `profiles/alsu/examples/<project>/hmi-export/`.
4. Keep every binding on controller-scope `HMI_*` tags; every device UDT gets exactly one faceplate.
5. `lf validate` then `lf hmi build`; report which profile rules were applied and which generic defaults
   remain because the profile is silent.

## Until the ALS-U HMI standard is loaded
Use the generic defaults, say so, and flag colour meanings, faceplate row order, and screen hierarchy
as items to align with the ALS-U standard once `standards/hmi.md` exists.
