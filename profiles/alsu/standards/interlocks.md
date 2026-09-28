# Interlock behaviour (AL-1605-0840 section 7)

Applies to every mitigation output and its permissives. All eight are **shall** requirements.

| Spec ID | Requirement |
|---|---|
| S09-07-095000 | When all permissive signals associated with a mitigation output are in their normal state, the PLC shall set the mitigation output to the permit/normal state, subject to S09-07-095020 and S09-07-095040. |
| S09-07-095010 | When any permissive associated with a mitigation output transitions to the trip state, the PLC shall set the mitigation output to the inhibit state. |
| S09-07-095020 | Once a trip event has occurred, the PLC shall hold the component or system in the trip state when the condition clears, until a reset (and in some cases an additional restart) action is taken by the operator. |
| S09-07-095030 | When any permissive transitions to the trip state, the PLC shall set that permissive's associated latch to the trip state. |
| S09-07-095040 | The latch shall remain in the trip state until a latch reset request is initiated by the operator. |
| S09-07-095050 | The PLC shall set to the trip state the first-fault signal associated with the first tripped permissive. |
| S09-07-095060 | In the event of a trip, the PLC shall set all other first-fault signals to the normal state. |
| S09-07-095070 | The first-fault signal shall remain in the trip state until a latch reset request is initiated by the operator OR a subsequent trip event occurs. |
| S09-07-095080 | First-fault signals will be reset on each trip event; archived data / event logs are used to investigate earlier trips. |

Plus from section 6: a **bypassed** permissive counts as permit, its raw `_Sts` and warning/trip bits
keep showing the real state, and its latch is in the permit state after a reset.

## Signal set per permissive (naming.md suffixes)
| Tag | Type | Meaning |
|---|---|---|
| `<Dev>_Sts` | BOOL | raw status, 1 = normal |
| `<Dev>_Byp` | BOOL | bypass, 1 = active |
| `<Dev>_Ltch` | BOOL | latched trip, 1 = tripped (held until reset) |
| `<Dev>_FF` | BOOL | first fault, 1 = this signal triggered the trip |
| `<Grp>_Rst` | BOOL | operator reset request (EPICS/HMI writes 1, PLC clears) |
| `<Grp>_Out` | BOOL | mitigation output, 1 = permit |

## LogixForge implementation
`templates/aois/PermLatch_AOI` implements one permissive (Sts, Byp, Rst in; Ltch, FF, Permit out)
against a group structure `UDT_PermGroup` that carries the group trip state used for first-fault
arbitration. The calling routine:
```
// Group trip state = any latch (evaluated before the AOIs so first-fault arbitration sees last scan)
[XIC(VVR1_Ltch),XIC(VVR2_Ltch),XIC(IP1_Ltch)]OTE(AR01_Grp.Trip_Sts);
// One AOI per permissive
PermLatch_AOI(VVR1_Perm,VVR1_Sts,VVR1_Byp,AR01_Rst,AR01_Grp,VVR1_Ltch,VVR1_FF,VVR1_Permit);
...
// Mitigation output permits only when no latch is set (S09-07-095000/010/020)
XIO(AR01_Grp.Trip_Sts)OTE(AR01_Out);
// Reset is a one-scan request from the operator; clear it after use
XIC(AR01_Rst)OTU(AR01_Rst);
```
The official ALS-U AOIs (e.g. `biLatch_AOI`) live in the ALS-U Controls Git repository and take
precedence over this template (S09-07-095380).
