# PLC diagnostics and health monitoring (AL-1605-0840 section 8.5)

| Spec ID | Requirement |
|---|---|
| S09-07-095380 | Engineers shall use the standard developed AOIs for data buffering and I/O module health monitoring. |
| S09-07-095390 | Diagnostic AOIs will be maintained with documentation in the ALS-U Git repository. |

- One diagnostic AOI per module type, named so purpose and type are obvious: `DIAG_IB16` for
  5069-IB16 / 5069-IB16F, and similarly for other modules.
- Primary function: collect and collate module health/diagnostics for the programmer (module fault,
  channel faults, connection status) so controls engineers and technicians can troubleshoot.
- Secondary function: **buffer the module's input and output data** for the program, guaranteeing
  inputs do not change within one evaluation of a program section (io-tags.md, S09-07-095290).
- Schedule the diagnostic/buffering program before control programs in the task (or in a faster
  periodic task).

LogixForge: until the official AOIs are added to `templates/aois/`, generate the buffering routine
explicitly (`CPS(Local:3:I.Data,R01S03DI,1)` style copies plus module `GSV(Module,...,EntryStatus)`)
and mark it in `docs/SPEC.md` as "to be replaced by DIAG_<module> AOIs from ALS-U Git".
