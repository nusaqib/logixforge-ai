---
name: plc-document-existing
description: Produce documentation for an existing Studio 5000 project that has no LogixForge spec - an .ACD/.L5X (and optionally a View Designer export) - as-built I/O list, tag list, routine map, cause-and-effect, alarm list, HMI tags, test plan, plus an agent-written as-built functional description. Use when the user says "document my existing project", "generate docs for this ACD/L5X", "what does this PLC program do", or wants to onboard a legacy project into LogixForge.
---

# Document an existing project

Two outcomes, pick with the user:
- **Docs only**: the project stays in Studio 5000; you deliver a `<name>_docs/` folder (fast, no repo).
- **Onboard**: the project becomes a LogixForge spec repository (`lf decompile`), docs live in `docs/generated/`
  and stay in step with future changes. Choose this when the project will be maintained through LogixForge.

## 1. Get the export
- Studio 5000: File > Save As > `.L5X` (whole controller). From a live controller: upload first, or use
  `plc-live-sdk` (`lf sdk upload-export`). Ask for the Logix version; note it in the report.
- HMI (optional): View Designer > File > Export Project > folder; PanelView ME/SE: not parsed, index the file.
- Put the export where the docs will live (docs only: any folder; onboard: `docs/input/` of the new repo after step 2).

## 2. Generate
```
# docs only
python -m logixforge.cli validate <export.L5X>              # errors here mean the export is unusual; report them
python -m logixforge.cli docs build <export.L5X> [-o <name>_docs]

# onboard
python -m logixforge.cli decompile <export.L5X> -o <repo>   # spec + modules/*.xml verbatim
python -m logixforge.cli init ... is NOT needed; add profile.json / naming.json by hand (copy from profiles/<site>/)
python -m logixforge.cli validate <repo>
python -m logixforge.cli docs ingest <repo> <export.L5X> --title "Studio 5000 export" --no-copy   # provenance row in INDEX.md
python -m logixforge.cli docs build <repo>
```
Generated set: `README.md`, `IO_LIST.md/.csv`, `TAGS.md`, `ROUTINES.md` (Mermaid task/program/routine tree,
call graph, rung index), `INTERLOCKS.md` (cause and effect from the ladder/ST, multiple-writer table),
`ALARMS.csv` (tag-based alarms, v31+ 5x80 only), `HMI_TAGS.md`, `TEST_PLAN.md` skeleton.

## 3. Write the as-built description (the part only you can do)
Create `SPEC.md` (docs only: in `<name>_docs/`; onboard: `docs/SPEC.md`) titled "<Controller> - as-built
functional description" with:
1. **Purpose and equipment** inferred from program/routine names, descriptions and rung comments; quote them.
2. **Structure**: paste the Mermaid tree from ROUTINES.md; state the scan order from each MainRoutine.
3. **I/O**: from IO_LIST.md; call out module points referenced directly in logic (no buffering).
4. **Behaviour per program**: read every routine with `lf inspect <export> --routine P/R`; describe modes,
   sequences, interlocks (cite INTERLOCKS.md rows), timers and setpoints with their values.
5. **Alarms and HMI interface**: ALARMS.csv + HMI_TAGS.md; if an HMI export exists, list its screens and
   which tags they bind (grep the `.hmi` files for `::` bindings).
6. **Findings**: run `lf validate <export>` and the `plc-review` method; list undocumented tags, duplicate
   writers (INTERLOCKS.md first table), uncalled routines, hard-coded values, missing descriptions.
7. **Open questions** you could not answer from the code; mark every inferred statement "(inferred)".
Never state an intent you cannot trace to a comment, description or rung; say "the code does X" instead.

## 4. Site profile
With a profile (ALS-U: `alsu-plc`), validate with the profile's `naming.json` (`LOGIXFORGE_NAMING=profiles/alsu/naming.json`
for docs-only) so the findings section lists deviations from the site standard with spec IDs.

## 5. Deliver
`lf docs export <repo> --to docx` (pandoc) when a document-control copy is wanted; otherwise hand over the
Markdown folder. Report: export version, what was generated, the size of the program (counts from
README.md), findings by severity, and what the user must confirm (inferred intents, open questions).
