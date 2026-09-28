"""Project documentation in both directions.

- ``extract``  : given documents (PDF, DOCX, XLSX, CSV, MD, images) -> ``docs/input/`` + ``docs/extracted/*.md`` + ``docs/INDEX.md``
- ``generate`` : spec -> ``docs/generated/*`` (I/O list, tags, routines, interlocks, alarms, HMI, test plan) with a spec hash stamp
- ``export``   : Markdown -> PDF/DOCX through pandoc (optional, external)
"""
from .extract import extract_text, ingest, read_index, spec_hash  # noqa: F401
from .generate import generate_docs, is_stale  # noqa: F401
