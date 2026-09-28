---
name: plc-aoi
description: Milestone 2 - design and write Logix Add-On Instructions (AOIs) in aois/<AOI_Name>/ (aoi.json + routines/Logic.rll or .st, optional Prescan/Postscan/EnableInFalse). Use when a device or algorithm pattern repeats (motor, valve, analog scaling, PID wrapper, sequencer) or when wrapping vendor logic.
---

# Add-On Instructions

## Layout
```
aois/AOI_Motor/aoi.json
aois/AOI_Motor/routines/Logic.rll          (required; .st allowed)
aois/AOI_Motor/routines/Prescan.rll        (optional, set execute_prescan)
aois/AOI_Motor/routines/Postscan.rll       (optional, SFC only)
aois/AOI_Motor/routines/EnableInFalse.rll  (optional, set execute_enable_in_false)
```
`aoi.json`:
```json
{ "name": "AOI_Motor", "revision": "1.0", "vendor": "Customer", "revision_note": "Initial",
  "description": "Single-direction motor with feedback supervision",
  "execute_prescan": false, "execute_enable_in_false": false,
  "parameters": [
    { "name": "Start", "data_type": "BOOL", "usage": "Input", "required": true, "description": "..." },
    { "name": "FaultDelay", "data_type": "DINT", "usage": "Input", "required": false, "default": 2000, "description": "ms" },
    { "name": "Run", "data_type": "BOOL", "usage": "Output", "required": true, "description": "..." },
    { "name": "Motor", "data_type": "UDT_Motor", "usage": "InOut", "description": "HMI interface (by reference)" }
  ],
  "local_tags": [ { "name": "T_Fault", "data_type": "TIMER", "description": "..." } ] }
```
## Rules (Logix)
- Input/Output parameters must be atomic (BOOL, SINT, INT, DINT, REAL...). Structures and arrays go
  through **InOut** (passed by reference, always required and visible).
- `EnableIn`/`EnableOut` are added automatically. Do not declare them.
- Rung text call includes the instance tag plus **required** parameters in definition order:
  `AOI_Motor(Conveyor01,Start,Stop,Feedback,Reset,Run,Fault);`. Non-required parameters are
  accessed via `Instance.Param`.
- Local tags are private (`ExternalAccess=None`). Inside the AOI, refer to parameters and locals by
  bare name. No JSR to program routines; no controller-scope tag access (except via InOut).
- AOI name <=40 chars, prefix `AOI_`; cannot be used in a UDT; can nest other AOIs.
- Changing parameters after deployment changes the instance layout (download). Add parameters at
  the end, bump `revision`, write `revision_note`.
- Routine must be named `Logic`. Output params keep last state when EnableIn is false unless
  `EnableInFalse` logic clears them; for motors, clear `Run` in EnableInFalse.

## Design guidance
- One AOI per device class (`AOI_Motor`, `AOI_Motor2Dir`, `AOI_Valve`, `AOI_AnalogIn`, `AOI_PIDWrap`).
- Interface: commands in, status out, config in via non-required inputs with sensible defaults, and an
  InOut UDT for the HMI faceplate so one instance tag binds the whole faceplate.
- Fault handling inside the AOI: detect, latch, reset only when cause cleared; expose `Fault` and a
  `FaultCode` DINT for HMI text lookup.
- Simulation support: `Sim` input that bypasses feedback supervision, used with `R_Sim` in Emulate.
- Test each AOI once in a small program (`P_Test_AOI`) with a truth table, then delete or disable it.

## Deliver
- `lf validate`: no `AOI_NO_LOGIC`, `AOI_PARAM_TYPE`, `AOI_OPERANDS`, `UNDEF_TAG` (in AOI scope this is
  an error because only parameters/locals are visible).
- Partial import for library sharing: `lf partial <project> --kind AddOnInstructionDefinition --name AOI_Motor`.
