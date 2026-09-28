# Terminology (AL-1605-0840 section 6)

Use these words with exactly these meanings in tag descriptions, rung comments, alarm text and HMI labels.

| Term | Definition |
|---|---|
| Alarm | Notification to an operator that a PV has fallen outside an acceptable range or entered an undesired status. May be based on warning or trip statuses. |
| Bypass | Flag to allow an input signal to be ignored in the PLC logic. The raw signal status and any warning/trip status bits continue to be shown. The latched status bit for a bypassed signal is in the PERMIT state after a RESET. **Bypass bits use positive polarity: logical high = bypass active.** |
| Clear | Set a status indication to logical low / 0. |
| Fail-safe | The state a device reverts to on breakdown, loss of power or malfunction; almost always de-energised. |
| Fault | Generic term covering any trip condition. |
| First fault | Per status bit, an associated bit indicating that this signal was the first fault identified by the PLC, i.e. the trigger of the protective action. Subsequent faults caused by the protective action do not get first-fault bits. Informational only. |
| Inhibit | Prevent operation of the external device or system. |
| Interlock | A fault status, usually tied to a sequence of events or protection logic, triggered when a process condition leaves a defined set of parameters. |
| Latch | Latch status bits indicate that a trip condition occurred on a signal. They remain set until the signal has recovered to normal **and** the operator requests a RESET of all latched bits. |
| Mitigation | An action that stops a device or machine from damage due to an interlock condition. |
| Normal | Signal state indicating no mitigation is required and equipment operation is permitted. |
| Permissive | A condition that must be satisfied to allow equipment or machine operation. |
| Permit | Allow operation of the external device or system. |
| Reset | Operator action (CS-Studio or HMI) that clears latched interlock and first-fault signals so an interlocked device can resume operation. |
| Set | Set a status indication to logical high / 1. |
| Status | Logical state of an input signal: high (1, true) or low (0, false). |
| Trip | A process or machine condition that requires the control system to take mitigation action. |
| Warning | Generates an alarm state but does not initiate automated mitigation. |

Convention that follows from the table: **status bits are positive-normal** (1 = normal / permit,
0 = trip) unless the tag description says otherwise, and every BOOL description states both states
(see documentation.md, S09-07-095420), e.g. "1 = Ok, 0 = Trip".
