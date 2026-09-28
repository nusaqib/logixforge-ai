# Documentation (AL-1605-0840 section 9)

| Spec ID | Requirement |
|---|---|
| S09-07-095400 | Ladder rungs, structured text lines and function block diagrams shall be commented to describe their necessity to the process or system. |
| S09-07-095410 | Comments should reference any relevant documents that dictate the control scheme being implemented. |
| S09-07-095420 | Boolean signals, both individual bits and array elements, should indicate signal state definitions in the tag description. |

- Comments say **why** the logic is needed, sufficient for another developer to understand function
  and intent. Always record unusual information, e.g. work-arounds for known vendor anomalies.
- Rung comments at the top of program sections and where appropriate inside routines reference the
  interface control documents, functional specifications and control scheme documents implemented.
- Every array element and every Boolean bit used in logic has a description; Boolean descriptions
  define both states, e.g. `0 = Ok, 1 = Fault` or `1 = Normal, 0 = Trip`.

LogixForge: the `//!` routine header names the governing document(s); rung comments cite spec IDs or
document numbers (`per AL-xxxx-xxxx 4.2`); the validator's NO_DESC checks cover tags and members,
and the ALS-U reviewer additionally checks that BOOL descriptions contain both state definitions.
