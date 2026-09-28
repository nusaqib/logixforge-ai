# Roadmap

## 0.1 (now)
- [x] Spec format, loader, rung parser, validator, L5X writer (full + partial), reader, decompile, diff
- [x] CLI, MCP server, plugin manifest, hooks (online guard, validate-on-write)
- [x] 15 milestone skills, 3 agents, 6 commands, standards docs, demo project, tests
- [x] Import `examples/conveyor-demo/build/ConveyorDemo.L5X` into Studio 5000 v33 with zero errors (2026-09-28)
- [ ] Verify Controller in Studio 5000 and run the demo in Logix Emulate
- [x] Tag-based alarm conditions from `alarms.json` (writer/reader/validator)
- [x] Studio 5000 View Designer HMI generator (`lf hmi build`): screens, AOG faceplates from UDTs, shortcuts
- [ ] Import the demo L5X (with AlarmConditions) and the View Designer folder; fix rejected names in `UNVERIFIED`
- [ ] Confirm Logix Designer SDK method names against an installed SDK; pin adapter

- [x] Site profile mechanism + ALS-U profile (AL-1605-0840 Rev B, masterCode reference project, masterHMI export)
- [x] Documentation layer: `lf docs ingest|build|export`, DOC_* validator rules, per-project repo scaffold (`lf init --git`)
- [x] SYSTEM.md overview and HMI_NAVIGATION.md (View Designer export reader); as-built docs for existing L5X projects
- [x] Toolkit hardened on a real v36 project: MOVE/EQ/... mnemonics, BIT members, module-defined types, /* */ ST comments, PowerLossProgram

## 0.2
- .hmi reader -> hmi.json (reference layouts, faceplate contracts); the structural half (screens, navigation, bindings,
  AOG use, security) exists in `logixforge/hmi/reader.py` and feeds HMI_NAVIGATION.md
- ALS-U: custom top bar generator, editing-mode gating, LED AOG reuse from the reference export
- Docs: SPEC.md section checks per profile, sequence tests derived from SPEC state tables, .dwg/.pdf drawing OCR via an external tool
- Module XML library (`templates/modules/`) for common 1756/5069/1734 modules and PowerFlex AOPs
- Emulate test harness: `lf test` runs pytest pycomm3 tests against Logix Emulate with sim tags
- Tag-based alarm definitions (v36+) and ALMD/ALMA generation from `Alm_` tags
- FBD routine authoring (sheet/block JSON -> FBDContent)
- CI workflow: validate + build on every PR, artefacts uploaded

## 0.3
- View Designer: popups, alarm-driven colour on faceplates, data logs, controller reference (Devices) file, per-screen security roles
- FactoryTalk View SE/ME display XML generation from the same hmi.json + faceplate contract
- FactoryTalk Optix project scaffolding
- PackML / ISA-88 phase and unit templates as AOIs + skills
- Multi-controller projects (produced/consumed consistency checks across specs)
