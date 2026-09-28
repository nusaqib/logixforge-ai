# PLC naming convention (AL-1605-0840 section 8.4, table 8.3)

Where a subsystem uses one generic program for several PLCs, the rack-location part of a name may be
omitted; the rest follows the format. Enforced (as NAME_STYLE warnings) by `profiles/alsu/naming.json`.

## Hardware components
| Type | Format | Example |
|---|---|---|
| Project file name (Git) | CPU name | `A0204_Vac`, `MPSA` |
| CPU | `<CommonPLCName>_<SubsystemName>` | `A0204_Vac`, `MPSA` |
| Communication | `<CPU Name>_<Rack#>` | `A0204_Vac_RIO2`, `MPSA1_RIO` |
| I/O modules | `<CPU Name>_<Rack##>_<ModuleType&Slot##>` | `A0204_Vac_R02_AI1` |
| HMI | `<CPUName>_HMI#` | `A0204_Vac_HMI` |

## Program components
| Type | Prefix | Format | Suffix | Example |
|---|---|---|---|---|
| Buffered I/O value | | `R##S##<CardType>[element]` | | `R01S03AI[3]`, `R01S04DI.2` |
| Tasks | `T##` (skip by 10s) | brief description, Pascal_Case_With_Underscores | | `T100_IO_Buffering` |
| Programs | `P##` (skip by 5s) | brief description | | `P100_AR01_Interlocks` |
| Routines | `R##` (skip by 5s) | brief description | | `R000_MainRoutine` |
| Add-On Instruction | | brief description of function | `_AOI` | `biLatch_AOI` (diagnostic AOIs: `DIAG_<module>`, see diagnostics.md) |
| Main (parent) UDT | `MainUDT_` | | | |
| Secondary (child) UDT | `UDT_` | brief description; use the individual-tag suffixes for members where possible | | `UDT_LLRF` |

## Individual tags (EPICS device name where possible; UDT-typed tags may be more generic)
| Signal | Suffix |
|---|---|
| UDT-typed tag | n/a |
| Boolean raw status | `_Sts` |
| Boolean latched status | `_Ltch` |
| Boolean first fault | `_FF` |
| Fault bypass | `_Byp` |
| Boolean command | `_Cmd` |
| Boolean output | `_Out` |
| Boolean selection | `_Sel` |
| Analog signal value | `_Val` |
| Analog signal value setpoint | `_SP` |
| Analog warning setpoint | `_H_SP` / `_L_SP` |
| Analog trip setpoint | `_HH_SP` / `_LL_SP` |
| Analog warning status bit | `_H_Sts` / `_L_Sts` |
| Analog trip status bit | `_HH_Sts` / `_LL_Sts` |
| Analog trip latched status bit | `_HH_Ltch` / `_LL_Ltch` |
| Reset bit | `_Rst` |
| Timer | `_Tmr` |
| One-shot storage bit | `_OSS` |
| EPICS array | brief description + `_<DataType>` | `GVLimit_bi[150]` |

Practical reading of the table:
- Device part first, EPICS style (`AR01C_VVR1`), then function, then suffix: `AR01C_VVR1_Opn_Cmd`.
- BOOL tags and UDT BOOL members end in one of `_Sts _Ltch _FF _Byp _Cmd _Out _Sel _Rst _OSS`
  (or the analog status forms `_H_Sts _L_Sts _HH_Sts _LL_Sts _HH_Ltch _LL_Ltch`).
- REAL/INT/DINT tags end in `_Val`, `_SP`, `_H_SP`, `_L_SP`, `_HH_SP`, `_LL_SP`.
- TIMER tags end in `_Tmr`; EPICS arrays end in the EPICS record type (`_bi _bo _ai _ao _mbbi ...`)
  or the data type (`_real _dint _int`).
- Buffered I/O tags `R##S##AI|AO|DI|DO...` are exempt from suffix rules.
