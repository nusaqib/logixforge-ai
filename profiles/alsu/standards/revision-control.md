# PLC revision control (AL-1605-0840 section 11)

| Spec ID | Requirement |
|---|---|
| S09-07-095470 | PLC engineers shall use the ALS-U PLC Revision Control processes for PLC project code. |

- Git on the in-house GitLab for version control; Rockwell Logix Designer Compare Tool for graphical
  diffs between PLC revisions. Details: ALS-U PLC Revision Control Workflow, AL-1605-0438 (not loaded).
- Project file name in Git = CPU name (naming.md), e.g. `A0204_Vac`.

LogixForge fit: the spec directory is text and diffs natively in GitLab; commit the spec, tag releases
with the L5X hash and controller serial (generic coding standard 24), and keep the exported L5X/ACD
alongside only if AL-1605-0438 requires it.
