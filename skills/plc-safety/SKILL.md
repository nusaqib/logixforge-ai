---
name: plc-safety
description: Milestone 8 - GuardLogix / Compact GuardLogix safety programming - safety task, safety programs and tags, certified safety instructions (ESTOP, DCS, SMAT, CROUT, safety I/O), signature and lock procedures, and the interlock rules standard logic must respect. Use whenever a project has safety-rated functions or a controller ending in S.
---

# Safety (GuardLogix)

**LogixForge writes the spec; a qualified safety engineer validates and signs.** Never claim a
safety function is validated. Safety logic is subject to the machine's risk assessment
(ISO 13849-1 PL / IEC 62061 SIL) and must be generated, tested and locked in Studio 5000.

## Structure
- `controller.json`: `"processor_type": "1756-L83ES"` (or `5069-L3xERMS`), `"safety": true`.
- `tasks.json`: `{ "name": "SafetyTask", "kind": "PERIODIC", "rate_ms": 20, "priority": 1, "watchdog_ms": 20,
  "programs": ["SafetyProgram"] }` (safety task is periodic, highest priority).
- `programs/SafetyProgram/program.json`: `"kind": "Safety"`; routines only ladder; safety tags in `tags.json`.
- Safety tags: use only atomic types and safety UDTs/AOIs; no aliases to standard tags; standard
  logic reads safety tags freely but can only write via **mapped** tags (Safety Tag Mapping in
  Studio 5000, standard -> safety, for reset/ack inputs). Mark mapped inputs `Std_` and
  document mapping in `docs/SAFETY.md`.

## Certified instructions (operands: see Rockwell 1756-RM095)
- `ESTOP(Estop_Tag)` with dual-channel inputs; `LC` light curtain; `SMAT` safety mat; `ENPEN` enable pendant;
  `TSAM/TSSM` two-hand; `DCS`/`DCST` dual-channel input stop (start/restart); `DCM` dual channel monitoring;
  `CROUT` configurable redundant output; `RIN`/`ROUT` redundant in/out; `SFX/SS1/SS2/SLS/SOS/STO` drive safety.
- Safety I/O: `1732ES`/`1734-IB8S`/`5069-IB8S` via test outputs, `.Pt00Data` style points; configure in Studio.
- Always: input reset behaviour (manual restart), output monitoring (EDM), fault reset via standard tag.

## Standard-side rules the generator must respect
- Every actuator output in `R_Outputs` is ANDed with the relevant safety status (`Safety_ZoneA_OK` from
  the safety program) even though the safety outputs cut power independently.
- No standard logic may fake a safety input; `Sim_` bits never touch safety tags.
- Alarms mirror safety states for HMI (`Alm_ESTOP_ZoneA`), read-only.

## Delivery checklist (in Studio 5000, by the safety engineer)
1. Import spec, configure safety I/O and mapping, verify.
2. Test every safety function against the validation plan (`docs/SAFETY.md`).
3. Generate safety signature, record it, lock the safety task; set safety lock password.
4. Any later change to safety logic invalidates the signature: re-validate.
LogixForge's `plc-review` skill flags standard logic that writes safety tags or bypasses safety gates.
