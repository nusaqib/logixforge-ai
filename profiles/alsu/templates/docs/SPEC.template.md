# <CPU name> - Subsystem PLC Specification (ALS-U)

Governing standard: ALS-U PLC Standardization Plan AL-1605-0840 (Rev __). Deviations from it are
listed in section 9 with justification (AL-1605-0840 section 5).

## 1 Subsystem and equipment
## 2 Controller and I/O (CPU name, racks `<CPU>_R##`, modules `<CPU>_R##_<Type><Slot>`, fail-safe output states, S09-07-095300/310)
## 3 Tasks and programs (periodic default S09-07-095220; T##/P##/R## numbering)
## 4 Interlock groups (per group: permissives with _Sts/_Byp/_Ltch/_FF, mitigation output `_Out`, reset `_Rst`; section 7 behaviour)
## 5 Analog signals (`_Val`, setpoints `_H_SP/_L_SP/_HH_SP/_LL_SP` owned by the PLC, EPICS alarm severities)
## 6 EPICS interface (controller tags only; input arrays < 500 bytes; outputs as individual tags; spreadsheet reference)
## 7 HMI (PanelView) screens and tags
## 8 Standard AOIs used (DIAG_<module>, marshalling, latch AOIs from ALS-U Git)
## 9 Deviations from AL-1605-0840
| Spec ID | Deviation | Justification | Approved by |
|---|---|---|---|
## 10 Open questions
