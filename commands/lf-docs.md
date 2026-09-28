---
description: Ingest given documents into a LogixForge project and/or regenerate its document set (I/O list, tags, routines, cause-and-effect, alarms, HMI tags, test plan)
argument-hint: [project_dir] [files-to-ingest...]
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

Load the `plc-documentation` skill. Project dir = first argument (default: nearest directory with
`controller.json`); any further arguments are documents to ingest.

1. For each document: `PYTHONPATH=${CLAUDE_PLUGIN_ROOT} python -m logixforge.cli docs ingest <dir> <file> --title ... --doc-no ... --rev ...`
   (ask for number/revision if the file name does not carry them). Read the `docs/extracted/*.md` result;
   for images, view the image and replace the stub with a written description and tables.
2. Move the extracted content into the spec (I/O -> tags/modules, interlocks -> routines with citations,
   alarms -> alarms.json, screens -> hmi/hmi.json, rules -> naming.json, the rest -> docs/SPEC.md).
3. `PYTHONPATH=${CLAUDE_PLUGIN_ROOT} python -m logixforge.cli validate <dir>` then
   `PYTHONPATH=${CLAUDE_PLUGIN_ROOT} python -m logixforge.cli docs build <dir>`.
4. Report: documents indexed (with what was mapped where and what is still open), generated files,
   validator summary, and the export command if a PDF/DOCX deliverable is wanted (`lf docs export`, needs pandoc).
