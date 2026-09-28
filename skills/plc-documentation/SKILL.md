---
name: plc-documentation
description: Project documentation in both directions for a LogixForge PLC/HMI project - ingest given documents (PDF, DOCX, XLSX, CSV, drawings/images) into docs/input + docs/extracted + docs/INDEX.md, turn their content into spec files, and generate the document set (I/O list, tag list, routine map, cause-and-effect, alarm list, HMI tags, test plan) from the spec with `lf docs build`; export to PDF/DOCX with pandoc. Use when the user hands over specifications, drawings, I/O lists or standards, asks for documentation, a test plan, an I/O list, or a deliverable document.
---

# Documentation

One repository per PLC project; the plugin repo holds only `examples/` and `profiles/`. Inside a project:
```
docs/
  INDEX.md       every given document: file, title, number, rev, date, kind, what it feeds, extraction
  input/         given documents as received (PDF, DOCX, XLSX, CSV, DWG/PDF, PNG); never edited
  extracted/     Markdown text of each input, made by `lf docs ingest`; the agent reads THIS, not the binary
  SPEC.md        functional specification, the one hand-maintained document (plc-project-setup milestone 0)
  generated/     `lf docs build` output, regenerated from the spec, committed, never hand-edited
  pandoc.yaml, reference.docx   optional export metadata/style (site profiles ship them)
```
Rule: **documentation given as input becomes spec files; documentation delivered as output is generated
from the spec.** Never maintain the same fact in two places.

## Ingest (documents in)
```
python -m logixforge.cli docs ingest <project> <file>... [--title T] [--doc-no AL-xxxx-xxxx] [--rev B] [--date YYYY-MM-DD] [--used-for "interlocks, naming"]
```
- Copies to `docs/input/`, writes `docs/extracted/<stem>.md`, upserts the `docs/INDEX.md` row.
- PDF needs `pip install pypdf`; DOCX/XLSX/CSV need nothing. Legacy `.doc` must be re-saved as `.docx`.
- Images and drawings get a stub: open the image yourself (Read tool), then replace the stub with a written
  description and Markdown tables of every signal, interlock and state you can read off it.
- Read `docs/extracted/*.md`, then move the content into the spec: I/O list rows -> `tags/*.json` aliases and
  `modules/*.xml` (from Studio 5000 exports), cause-and-effect matrix -> interlock logic in `.rll` with the
  document cited in rung comments, alarm lists -> `alarms.json`, HMI screen lists -> `hmi/hmi.json`,
  naming rules -> `naming.json`, everything else -> `docs/SPEC.md` sections with the source cited
  ("per AL-1605-0840 S09-07-095290"). Mark what could not be mapped under "Open questions" in SPEC.md.
- Large drawings: keep in `docs/input/` under Git LFS (`*.dwg`, big PDFs) or reference the document
  system location in INDEX.md with `--no-copy`.

## Generate (documents out)
```
python -m logixforge.cli docs build <project> [--hmi <View Designer export>]   # -> docs/generated/
python -m logixforge.cli docs export <project> --to docx|pdf|html [-o file] [file.md ...]   # pandoc
```
`docs/generated/` = `README.md` (index and counts), **`SYSTEM.md`** (system overview: identification,
architecture diagram with chassis/remote racks/IPs/HMI, hardware inventory, networks and comms instructions,
control software, operator interface, external data interface, document set), `IO_LIST.md/.csv`, `TAGS.md`
(UDTs, AOIs, tags), `ROUTINES.md` (task/program/routine tree and call graph as Mermaid, rung index),
`INTERLOCKS.md` (cause and effect derived from the logic, multiple-writer table), `ALARMS.csv`, `HMI_TAGS.md`,
**`HMI_NAVIGATION.md`** (screen hierarchy by folder, menu shortcuts, banner, navigation graph, reachability
checks, Add-On Graphic usage, bindings per screen; from `hmi/hmi.json` or a View Designer export found at
`<project>/hmi-export`, `docs/input/*/ViewApplication.hmi` or `--hmi`), `TEST_PLAN.md` (one case per output,
alarm and screen; sequence tests are added by hand from SPEC.md).
SYSTEM.md is the inventory; the narrative system overview (purpose, physical layout, operating concept) is
section 0 of `docs/SPEC.md` and must reference SYSTEM.md rather than repeat its tables.
Every file carries the spec hash; `lf validate` reports `DOC_STALE` when the spec changed after the last
build, so rebuild before every commit and before review. Markdown is canonical (diffable, renders on
GitHub); PDF/DOCX are export targets for document control only.

## Existing projects
For a project that exists only as an ACD/L5X (no spec), use `plc-document-existing`: `lf docs build file.L5X`
works directly on the export, and `lf decompile` turns it into a spec repo when it is to be maintained here.

## Review use
- `INTERLOCKS.md` is what the code does; `SPEC.md` is what it must do. Diff them by hand in `plc-review`.
- `TEST_PLAN.md` is the FAT/SAT record; fill Result and Tester columns in a copy under `tests/`.

## Validator codes
`DOC_SPEC` (missing/placeholder spec), `DOC_INPUT_UNINDEXED` (file in docs/input not in INDEX.md),
`DOC_NOT_EXTRACTED` (no extracted text), `DOC_STALE` (generated older than spec), `DOC_NONE` (never generated).

## Site profiles
Profiles add their document template and export metadata under `profiles/<name>/templates/docs/`
(ALS-U: `SPEC.template.md`, `pandoc.yaml` with the AL document-number/revision block) and their
documentation rules in `standards/documentation.md`. Load `<profile>-plc` first when a profile is set.
