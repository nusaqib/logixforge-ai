"""Markdown -> PDF / DOCX / HTML through pandoc (external, optional).

pandoc is not a Python dependency; install it from https://pandoc.org (PDF output also needs a LaTeX
engine, or use `--pdf-engine=wkhtmltopdf`/`weasyprint`). A site profile can ship a `docs/pandoc.yaml`
metadata block (title page, document number, revision table) and a `reference.docx` style template.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

FORMATS = {"pdf": ".pdf", "docx": ".docx", "html": ".html"}


def pandoc_available() -> str | None:
    return shutil.which("pandoc")


def export_markdown(md_files: list[str | Path], fmt: str, output: str | Path, *, metadata: str | Path | None = None,
                    reference_docx: str | Path | None = None, pdf_engine: str = "", toc: bool = True) -> Path:
    """Concatenate `md_files` (in order) and run pandoc. Raises RuntimeError when pandoc is missing."""
    exe = pandoc_available()
    if not exe:
        raise RuntimeError("pandoc not found on PATH; install it from https://pandoc.org or hand the Markdown to the document owner")
    if fmt not in FORMATS:
        raise RuntimeError(f"unsupported export format {fmt!r}; use one of {', '.join(FORMATS)}")
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [exe, *[str(Path(f)) for f in md_files], "-o", str(out), "--from", "gfm", "--standalone"]
    if toc:
        cmd.append("--toc")
    if metadata:
        cmd += ["--metadata-file", str(Path(metadata))]
    if fmt == "docx" and reference_docx:
        cmd += ["--reference-doc", str(Path(reference_docx))]
    if fmt == "pdf" and pdf_engine:
        cmd += ["--pdf-engine", pdf_engine]
    if fmt == "html":
        cmd += ["--embed-resources"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"pandoc failed ({r.returncode}): {r.stderr.strip()}")
    return out


def project_export(root: str | Path, fmt: str, output: str | Path | None = None, files: list[str] | None = None,
                   pdf_engine: str = "") -> Path:
    """Export SPEC.md + the generated set (or `files`, relative to docs/) of a project as one document."""
    root = Path(root)
    docs = root / "docs"
    if files:
        md = [docs / f for f in files]
    else:
        gen = docs / "generated"
        md = [docs / "SPEC.md"] + [gen / n for n in ("IO_LIST.md", "TAGS.md", "ROUTINES.md", "INTERLOCKS.md", "HMI_TAGS.md", "TEST_PLAN.md")]
    md = [m for m in md if m.exists()]
    if not md:
        raise RuntimeError("nothing to export: run `lf docs build` first or pass --files")
    meta = docs / "pandoc.yaml"
    ref = docs / "reference.docx"
    name = root.name
    cj = root / "controller.json"
    if cj.exists():
        import json
        name = json.loads(cj.read_text(encoding="utf-8")).get("name", name)
    out = Path(output) if output else root / "build" / "docs" / f"{name}{FORMATS[fmt]}"
    return export_markdown(md, fmt, out, metadata=meta if meta.exists() else None,
                           reference_docx=ref if ref.exists() else None, pdf_engine=pdf_engine)
