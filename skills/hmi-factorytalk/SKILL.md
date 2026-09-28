---
name: hmi-factorytalk
description: Roadmap placeholder for FactoryTalk View SE/ME and FactoryTalk Optix HMI generation. Use when the user asks for those platforms; explains what LogixForge provides today (HMI tag interface, alarm CSV, View Designer generator) and how to proceed manually.
---

# FactoryTalk View SE/ME and Optix (roadmap)

The primary HMI target is Studio 5000 View Designer (see `hmi-view-designer`). For FactoryTalk platforms
LogixForge currently provides:
- `python -m logixforge.cli hmi docs <project>` -> `docs/HMI_TAGS.md` (tag interface with directions)
  and `docs/ALARMS.csv` (tag-based alarm list; FactoryTalk Alarms & Events reads the same controller alarms).
- The faceplate contract (`hmi/hmi.json` faceplates, derived from UDTs) that a View SE/ME Global Object
  or an Optix type should implement.

Manual path today: create one Global Object (View) or one Type (Optix) per device UDT with the members
listed in `HMI_TAGS.md`, bind via FactoryTalk Linx shortcut `{[Shortcut]HMI_Conveyor01.Sts_Run}` (View) or
the Logix driver tag importer (Optix), and use the ALARMS.csv for the alarm summary configuration.

Planned: View ME/SE display XML generation from the same `hmi.json`, Optix project scaffolding.
