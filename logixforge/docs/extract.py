"""Ingest given documents into a project: keep the original in docs/input/, write a Markdown text
extraction to docs/extracted/ (what the agent reads) and record it in docs/INDEX.md.

Formats: .pdf (pypdf, optional), .docx / .xlsx (stdlib zipfile + XML, no extra packages),
.csv / .md / .txt (copied), images (.png/.jpg/.svg -> stub that tells the agent to view and describe it).
"""
from __future__ import annotations

import csv
import hashlib
import io
import re
import shutil
import zipfile
from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET

INDEX_COLUMNS = ["File", "Title", "Document no.", "Rev", "Date", "Kind", "Used for", "Extracted"]
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".tif", ".tiff"}
TEXT_EXT = {".md", ".txt", ".csv", ".json", ".rll", ".st", ".l5k"}
SPEC_SKIP_DIRS = {"docs", "build", "tests", ".git", "__pycache__", ".venv", "hmi-export"}

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
S = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


# ------------------------------------------------------------------ spec hash

def spec_hash(root: str | Path) -> str:
    """SHA-256 over every spec file (everything except docs/, build/, tests/). Used by the DOC_STALE rule."""
    root = Path(root)
    h = hashlib.sha256()
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root)
        if not p.is_file() or any(part in SPEC_SKIP_DIRS for part in rel.parts):
            continue
        h.update(rel.as_posix().encode()); h.update(b"\0")
        h.update(p.read_bytes()); h.update(b"\0")
    return h.hexdigest()[:16]


# ------------------------------------------------------------------ extractors

def _pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError:
        raise RuntimeError("PDF extraction needs pypdf: pip install pypdf (or paste the text manually into docs/extracted/)")
    rd = PdfReader(str(path))
    parts = []
    for i, page in enumerate(rd.pages, 1):
        txt = (page.extract_text() or "").strip()
        parts.append(f"<!-- page {i} -->\n{txt}")
    return "\n\n".join(parts)


def _docx_table(tbl) -> list[str]:
    rows = []
    for tr in tbl.iter(W + "tr"):
        cells = []
        for tc in tr.findall(W + "tc"):
            cells.append(" ".join("".join(t.text or "" for t in p.iter(W + "t")).strip() for p in tc.findall(W + "p")).replace("|", "\\|"))
        rows.append("| " + " | ".join(cells) + " |")
    if rows:
        rows.insert(1, "|" + "---|" * (rows[0].count("|") - 1))
    return rows


def _docx(path: Path) -> str:
    with zipfile.ZipFile(path) as z:
        body = ET.fromstring(z.read("word/document.xml")).find(W + "body")
    out = []
    for el in body:
        if el.tag == W + "p":
            style = el.find(f"{W}pPr/{W}pStyle")
            sv = (style.get(W + "val") if style is not None else "") or ""
            text = "".join(t.text or "" for t in el.iter(W + "t")).strip()
            if not text:
                continue
            m = re.match(r"(?i)heading(\d)", sv)
            if m:
                out.append("#" * int(m.group(1)) + " " + text)
            elif sv.lower() == "title":
                out.append("# " + text)
            elif el.find(f"{W}pPr/{W}numPr") is not None:
                out.append("- " + text)
            else:
                out.append(text)
            out.append("")
        elif el.tag == W + "tbl":
            out += _docx_table(el) + [""]
    return "\n".join(out)


def _col_index(ref: str) -> int:
    n = 0
    for ch in re.match(r"[A-Z]+", ref).group(0):
        n = n * 26 + ord(ch) - 64
    return n - 1


def _xlsx(path: Path) -> str:
    with zipfile.ZipFile(path) as z:
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            for si in ET.fromstring(z.read("xl/sharedStrings.xml")).iter(S + "si"):
                shared.append("".join(t.text or "" for t in si.iter(S + "t")))
        wb = ET.fromstring(z.read("xl/workbook.xml"))
        rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        rid_to_target = {r.get("Id"): r.get("Target") for r in rels}
        out = []
        for sh in wb.iter(S + "sheet"):
            rid = sh.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
            target = rid_to_target.get(rid, "")
            target = target if target.startswith("xl/") else "xl/" + target.lstrip("/")
            if target not in z.namelist():
                continue
            rows: list[list[str]] = []
            for row in ET.fromstring(z.read(target)).iter(S + "row"):
                cells: dict[int, str] = {}
                for c in row.findall(S + "c"):
                    v = c.find(S + "v")
                    val = v.text if v is not None else ""
                    if c.get("t") == "s" and val:
                        val = shared[int(val)]
                    elif c.get("t") == "inlineStr":
                        val = "".join(t.text or "" for t in c.iter(S + "t"))
                    cells[_col_index(c.get("r", "A1"))] = (val or "").replace("|", "\\|").replace("\n", " ")
                if cells:
                    width = max(cells) + 1
                    rows.append([cells.get(i, "") for i in range(width)])
            out.append(f"## Sheet: {sh.get('name')}")
            out.append("")
            if rows:
                width = max(len(r) for r in rows)
                rows = [r + [""] * (width - len(r)) for r in rows]
                out.append("| " + " | ".join(rows[0]) + " |")
                out.append("|" + "---|" * width)
                out += ["| " + " | ".join(r) + " |" for r in rows[1:]]
            out.append("")
    return "\n".join(out)


def _csv(path: Path) -> str:
    rows = list(csv.reader(io.StringIO(path.read_text(encoding="utf-8-sig"))))
    if not rows:
        return ""
    width = max(len(r) for r in rows)
    rows = [[c.replace("|", "\\|") for c in r] + [""] * (width - len(r)) for r in rows]
    return "\n".join(["| " + " | ".join(rows[0]) + " |", "|" + "---|" * width] + ["| " + " | ".join(r) + " |" for r in rows[1:]])


def _image(path: Path) -> str:
    return (f"![{path.name}]({path.name})\n\n"
            "<!-- Diagram: open the image (Read tool / viewer) and replace this block with a written description: "
            "what equipment it shows, every tag/signal name visible, interlock chains, states and transitions. "
            "Put any tabular data (I/O points, cause-and-effect) in a Markdown table so it can become spec files. -->\n")


def extract_text(path: str | Path) -> str:
    """Return a Markdown text rendering of a document. Raises RuntimeError for unsupported/missing tools."""
    p = Path(path)
    ext = p.suffix.lower()
    if ext == ".pdf":
        return _pdf(p)
    if ext == ".docx":
        return _docx(p)
    if ext == ".xlsx":
        return _xlsx(p)
    if ext == ".csv":
        return _csv(p)
    if ext in TEXT_EXT:
        return p.read_text(encoding="utf-8-sig", errors="replace")
    if ext in IMAGE_EXT:
        return _image(p)
    if ext == ".doc":
        raise RuntimeError(f"{p.name}: legacy .doc is not supported; save it as .docx or .pdf first")
    raise RuntimeError(f"{p.name}: unsupported format {ext!r}")


# ------------------------------------------------------------------ INDEX.md

def index_path(root: str | Path) -> Path:
    return Path(root) / "docs" / "INDEX.md"


def _index_header(name: str) -> str:
    return (f"# {name} - document index\n\n"
            "Every given document lives in `docs/input/` and is listed here with its number and revision; the agent "
            "reads the Markdown text in `docs/extracted/`. Generated documents are in `docs/generated/` (`lf docs build`).\n\n"
            "| " + " | ".join(INDEX_COLUMNS) + " |\n|" + "---|" * len(INDEX_COLUMNS) + "\n")


def read_index(root: str | Path) -> list[dict]:
    """Rows of docs/INDEX.md as dicts keyed by INDEX_COLUMNS (empty list when absent)."""
    ip = index_path(root)
    if not ip.exists():
        return []
    rows = []
    for line in ip.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells or cells[0] in ("File", "") or set(cells[0]) <= {"-"}:
            continue
        cells += [""] * (len(INDEX_COLUMNS) - len(cells))
        rows.append(dict(zip(INDEX_COLUMNS, cells)))
    return rows


def write_index(root: str | Path, rows: list[dict], name: str = "") -> Path:
    ip = index_path(root)
    ip.parent.mkdir(parents=True, exist_ok=True)
    if not name:
        name = ip.parent.parent.name
        cj = ip.parent.parent / "controller.json"
        if cj.exists():
            import json
            name = json.loads(cj.read_text(encoding="utf-8")).get("name", name)
    text = _index_header(name)
    for r in rows:
        text += "| " + " | ".join(str(r.get(c, "")).replace("|", "\\|") for c in INDEX_COLUMNS) + " |\n"
    ip.write_text(text, encoding="utf-8")
    return ip


# ------------------------------------------------------------------ ingest

def ingest(root: str | Path, source: str | Path, *, title: str = "", doc_no: str = "", rev: str = "",
           doc_date: str = "", used_for: str = "", copy: bool = True) -> dict:
    """Copy `source` to docs/input/, extract to docs/extracted/<stem>.md, upsert the INDEX row.
    Returns {"input": Path, "extracted": Path|None, "error": str}. Extraction failure still indexes the file."""
    root = Path(root)
    src = Path(source)
    if not src.is_file():
        raise FileNotFoundError(src)
    in_dir, ex_dir = root / "docs" / "input", root / "docs" / "extracted"
    in_dir.mkdir(parents=True, exist_ok=True); ex_dir.mkdir(parents=True, exist_ok=True)
    dst = in_dir / src.name
    if copy and src.resolve() != dst.resolve():
        shutil.copy2(src, dst)
    elif not dst.exists():
        dst = src
    sha = hashlib.sha256(dst.read_bytes()).hexdigest()[:12]
    ex_path = ex_dir / (src.stem + ".md")
    error = ""
    try:
        body = extract_text(dst)
        head = (f"<!-- extracted by lf docs ingest from docs/input/{dst.name} (sha256 {sha}) on {date.today().isoformat()};"
                " edit freely: this is the agent's working copy, the original is the reference -->\n")
        ex_path.write_text(head + f"# {title or src.stem}\n\n" + body.rstrip() + "\n", encoding="utf-8")
        if dst.suffix.lower() in IMAGE_EXT:
            shutil.copy2(dst, ex_dir / dst.name)     # so the image link in the .md resolves
    except RuntimeError as e:
        error = str(e)
        ex_path = None
    rows = read_index(root)
    rel = f"input/{dst.name}" if dst.parent == in_dir else str(dst)
    row = {"File": rel, "Title": title or src.stem, "Document no.": doc_no, "Rev": rev,
           "Date": doc_date or date.today().isoformat(), "Kind": dst.suffix.lower().lstrip("."),
           "Used for": used_for, "Extracted": f"extracted/{ex_path.name}" if ex_path else f"NOT EXTRACTED: {error}"}
    for i, r in enumerate(rows):
        if r["File"] == rel:
            for k in ("Title", "Document no.", "Rev", "Date", "Used for"):
                if not row[k]:
                    row[k] = r.get(k, "")
            rows[i] = row
            break
    else:
        rows.append(row)
    write_index(root, rows)
    return {"input": dst, "extracted": ex_path, "error": error, "sha256": sha}
