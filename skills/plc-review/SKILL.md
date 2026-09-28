---
name: plc-review
description: Milestone 9 - review Studio 5000 code (LogixForge spec or an exported/uploaded .L5X) for correctness, safety, standards compliance and maintainability. Use when asked to review, audit, compare, or check PLC code, or before delivering a build. Produces findings ranked by severity with rung-level references.
---

# PLC code review

## Inputs
- Spec dir or `.L5X` (from Studio 5000 export or controller upload). For an ACD, ask the user to
  export L5X (File > Save As > L5X) or use `plc-live-sdk` upload.
- `python -m logixforge.cli validate <path> --json` for mechanical findings.
- `python -m logixforge.cli inspect <path> --routine P/R` to read rungs.
- `python -m logixforge.cli diff <before> <after>` for change reviews.
- Checklist: `${CLAUDE_PLUGIN_ROOT}/standards/review-checklist.md`.

## Method
1. Run the validator; triage errors (blocking) and warnings.
2. Read `MainRoutine` of every program to learn scan order, then each routine top to bottom.
3. For each output (OTE/OTL/assignment) find every writer. Duplicate writers are Critical.
4. Trace every safety-relevant output back to its permissives.
5. Check timers/counters/one-shots for storage-bit reuse and missing resets.
6. Check state machines for unreachable states, missing abort paths, missing timeouts.
7. Check alarms: each fault has an alarm, each alarm has ack/reset logic and HMI text.
8. Check naming, descriptions, rung comments, dead code (routine uncalled, tags unused).
9. Check I/O mapping isolation, simulation bits, forces left on (`Force` elements in L5X).
10. Check task load: periodic tasks with heavy loops, `FOR`/`WHILE` bounds, `COP` sizes.

## Output format
```
## Summary  (1-3 sentences, ship / do not ship)
## Findings
### Critical  - will fault, unsafe, or wrong behaviour
- [P_Conveyor/R_Outputs rung 3] O_Motor driven from two OTEs (also R_Conveyor rung 8). Fix: ...
### Major     - functional gap, standards violation with operational impact
### Minor     - maintainability, naming, comments
### Info      - suggestions
## Verified by tooling vs. needs Studio 5000
```
Every finding names program/routine/rung (or tag), states the failure scenario, and gives a fix.
Do not report style issues as Critical. If the code is fine, say so and list what you checked.

## Applying fixes
Only when asked. Edit the spec (never the L5X), re-run validate/build, and produce a `lf diff`
between old and new build for the user.
