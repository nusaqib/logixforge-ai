---
name: plc-io-modules
description: Milestone 4 - add I/O modules, drives and remote adapters to a LogixForge project (modules/*.xml from Studio 5000 exports, RPI, EKey, connection formats) and wire alias tags to module I/O. Use when configuring the I/O tree or when alias tags reference Local:x:I / remote adapters.
---

# I/O modules and drives

Module definitions (`<Module>` in L5X) contain connection formats, config data blobs and product
codes that only the Studio 5000 module profile knows. **LogixForge does not synthesise them.**
Get them from Studio 5000 and inline them.

## Procedure
1. In Studio 5000 (any project of the same firmware major revision) add the module in the I/O tree
   with the intended slot/IP, connection format, RPI and electronic keying.
2. Right-click the module > **Export Module...** (or export the project as L5X and copy the element).
3. Save the full `<Module ...> ... </Module>` element as `modules/<ModuleName>.xml`. Keep child
   elements (`EKey`, `Ports`, `Communications` with `ConfigTag`, `Connections`, `ExtendedProperties`).
4. Check `ParentModule` / `ParentModPortId` / `Address` match your chassis plan. For remote racks the
   adapter (e.g. `1756-EN2TR`, `1734-AENTR`) is a module too, with the I/O modules as children.
5. Re-run `lf build`; the writer inlines the XML verbatim. The controller's own `Local` module is
   never emitted (Studio 5000 creates it from the processor type; emitting it collides and fails).
   Alias tags `Local:2:I.Data.0`, `Rack1:1:I.Ch0Data` become valid.

Minimal JSON fallback (`modules.json`) exists for planning only; it will not import for real modules:
```json
[{ "name": "DI_Slot2", "catalog_number": "1756-IB16", "parent": "Local", "address": "2", "port_type": "ICP" }]
```

## Design rules
- Naming: `<Type>_<Location>`: `DI_Slot2`, `DO_Slot3`, `AI_Slot4`, `EN2TR_Line1`, `VFD_Conveyor01`,
  `PF525_Pump02`, `AENTR_Rack1`. Descriptions with panel/drawing reference.
- RPI: discrete 10-20 ms, analog 50-100 ms, drives 20 ms, safety 10-20 ms; do not go faster than
  needed (network load).
- EKey: `CompatibleModule` in production; `ExactMatch` only if validated; `Disabled` never.
- Connection type: use `Data` (not `Full Diagnostics`) unless diagnostics are consumed; for drives
  prefer `Add-On Profile` datalinks over generic modules.
- `Inhibited: false`, `MajorFault: false` for non-critical I/O (controller keeps running on I/O loss and
  logic handles the fault via `GSV(Module,<Name>,EntryStatus,...)` or `.ConnectionFaulted`).
- Map module fault bits into alarms (`Alm_IO_Rack1_Fault`).

## I/O tags and aliases
- Alias per point in `tags/io.json` with the panel wire tag in the description.
- Analog inputs: keep raw `AI_` alias plus scaled program tag via `AOI_AnalogIn`.
- Outputs: alias `O_` and drive only from `R_Outputs`.

## Done when
Every alias target resolves (`lf validate` no `ALIAS_TARGET` warnings), module XML present for each
slot in the I/O list, RPI/keying recorded in `docs/SPEC.md`.
