# I/O handling and tag data (AL-1605-0840 section 8.3)

| Spec ID | Requirement |
|---|---|
| S09-07-095290 | Analog and discrete input data shall be buffered into a separate tag before it is used within the PLC program. (Rev B open comment on wording; intent: copy raw module data to a buffer tag once per scan and use only the buffer.) |
| S09-07-095300 | Analog and discrete output modules or data shall be configured to set the values to a known fail-safe state in the event of a fault. |
| S09-07-095310 | If an output must be set to anything other than zero (off, logical low) during a fault it shall be documented in the subsystem design documentation. |
| S09-07-095320 | UDTs should be used to organise tags within a PLC program. |
| S09-07-095330 | Marshalling for structures should be encapsulated in add-on instructions or parameterised functions. |
| S09-07-095340 | Tags that require EPICS access shall be set as controller tags. |
| S09-07-095350 | Program tags should be used when access is not required outside a given program. |
| S09-07-095360 | Tags shall be named or aliased such that they are meaningful to their use in the control application. |
| S09-07-095370 | Controller tag names should resemble the associated EPICS name when used in the control application. |

## Inputs (8.3.1)
Logix reads inputs asynchronously; values can change mid-scan. All analog and discrete inputs are
buffered (snapshot) so sequence-dependent logic sees a time-consistent set. The DIAG_ AOIs do this
buffering (diagnostics.md). Buffer tags are named `R##S##<CardType>[n]` (naming.md), e.g.
`R01S03AI[3]`, `R01S04DI.2`, and aliased to EPICS-like names for use in logic.

LogixForge mapping: the `R_Inputs`-style routine of the generic standard becomes the buffering
routine (`R005_IO_Buffering` or the DIAG_ AOI calls); control routines never reference `Local:x:I`.

## Outputs (8.3.2)
Module fault state = off/zero unless documented otherwise. Configure in the module XML
(`modules/*.xml` from a Studio 5000 export) and state exceptions in `docs/SPEC.md`.

## Tag organisation (8.3.3)
| Use | Data type |
|---|---|
| Analog device in floating-point mode / floating-point number | REAL |
| Analog device in integer mode | INT |
| ASCII characters | STRING |
| Digital I/O point or bit | BOOL |
| Integer | DINT / INT |

- UDTs organise all data of a subsystem aspect into one tag; a standard UDT set is maintained in the
  ALS-U Controls Git with EPICS substitution files. UDTs and predefined structures must be broken
  down to base types for EPICS (epics.md).
- Arrays for indexed access (input buffers) and for read-only EPICS transfer.
- Marshalling (structure <-> linear array) lives in AOIs or parameterised functions.
- Controller scope only for data EPICS or other programs need; everything else program scope.

## Tag naming (8.3.4)
Alias tags keep logic readable when the data lives in generically named buffers or transfer arrays.
Name progression example (table 8.2):

| Raw data tag | Buffered tag (alias) | EPICS-like PLC tag |
|---|---|---|
| `Local:5:O.Pt00.Data` | `R01S05DO.0` | `AR01C_VVR1_Opn_Cmd` |

Controller tag names follow the EPICS device name where possible (S09-07-095370); see naming.md.
