# PLC / IOC configuration (AL-1605-0840 section 10)

## Data transfer (10.1)
| Spec ID | Requirement |
|---|---|
| S09-07-095430 | EPICS input data from the PLC should be packaged and transferred as array tags. |
| S09-07-095440 | Array tag sizes shall be maintained under 500 bytes. |
| S09-07-095450 | EPICS output data to the PLC shall be maintained as individual tags. |
| S09-07-095460 | PLC tags that must be accessed by the IOC will be documented in a standard spreadsheet for EPICS database creation. |

- Transport: EtherNet/IP with the EPICS "EtherIP" driver. The IOC reads any **non-UDT controller
  tag**, including module I/O tags; it cannot read program tags. Scalar BOOL, SINT, INT, DINT, REAL
  and array elements of those types.
- ~8 ms per tag transfer; the driver merges element requests into whole-array reads, so pack PLC ->
  EPICS data into arrays (REAL[40] costs little more than one REAL). Driver buffer limit 500 bytes
  (REAL/DINT[125], INT[250], BOOL[4000 bits] max; keep margin).
- EPICS -> PLC writes: individual tags only (array writes replace the whole array).
- The PLC engineer fills in the standard tag spreadsheet; the IOC engineer converts it to an EPICS db.

## Alarm handling (10.2, added in Rev B)
- The EPICS alarm handler is the primary alarm system. **The PLC is the maintainer of alarm
  setpoints**; PLC setpoint tags (`_H_SP _L_SP _HH_SP _LL_SP`) are written to the LOW/LOLO/HIGH/HIHI
  fields of the EPICS records.
- The PLC may compare PVs against those thresholds for interlocks or HMI display, but those results
  are not used by the EPICS alarm handler. MAJOR/MINOR severities are set in EPICS: warning PVs ~
  MINOR, trip PVs ~ MAJOR.
- Reference: ALS-U Controls Alarm Philosophy AL-1692-1312 (not yet loaded into this profile).

LogixForge consequences:
- `alarms.json` (Logix tag-based alarms) is for the **PanelView HMI only**; do not present it as the
  alarm system. Severities in `alarms.json` mirror EPICS: trip -> 800 (MAJOR-like), warning -> 400 (MINOR-like).
- Generate `docs/EPICS_TAGS.csv` (controller tags with type, dimension, direction, description) as
  the starting point for the standard spreadsheet; the validator warns when an array exceeds 500 bytes
  or when an EPICS-facing tag is program-scoped or UDT-typed.
