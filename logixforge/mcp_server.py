"""LogixForge MCP server - exposes the toolkit to any MCP-capable agent (Claude Code, Cursor, etc.).

Run:  python -m logixforge.mcp_server            (stdio transport)
Needs: pip install logixforge[mcp]

Tools are deliberately coarse and side-effect-explicit. Offline tools never touch a controller.
Online tools require LOGIXFORGE_ALLOW_ONLINE_WRITE=1 for anything that writes.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

try:                                   # mcp 2.x renamed FastMCP -> MCPServer; the API we use is identical
    from mcp.server.mcpserver import MCPServer as FastMCP
except ImportError:  # pragma: no cover
    try:
        from mcp.server.fastmcp import FastMCP  # mcp 1.x
    except ImportError:
        FastMCP = None

from .l5x.reader import export_project_dir, read_l5x
from .l5x.writer import project_summary, write_l5x, write_partial
from .project import load_project
from .rll import RungSyntaxError, instruction_names, operand_tags, parse_rung
from .validate import validate

mcp = FastMCP("logixforge") if FastMCP else None


def _tool(fn):
    return mcp.tool()(fn) if mcp else fn


@_tool
def lf_validate(path: str) -> str:
    """Validate a LogixForge project directory or an .L5X file. Returns findings as JSON."""
    p = Path(path)
    proj = load_project(p) if p.is_dir() else read_l5x(p)
    naming = {}
    if p.is_dir() and (p / "naming.json").exists():
        naming = json.loads((p / "naming.json").read_text(encoding="utf-8"))
    return json.dumps([f.__dict__ for f in validate(proj, naming)], indent=2)


@_tool
def lf_build(project_dir: str, output: str = "", partials: bool = False) -> str:
    """Build a full-controller L5X (and optionally partial-import files) from a project directory."""
    proj = load_project(project_dir)
    errs = [f for f in validate(proj) if f.level == "error"]
    if errs:
        return "BUILD BLOCKED by validation errors:\n" + "\n".join(str(e) for e in errs)
    out = output or str(Path(project_dir) / "build" / f"{proj.controller.name}.L5X")
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    write_l5x(proj, out)
    written = [out]
    if partials:
        pdir = Path(out).parent / "partial"
        pdir.mkdir(exist_ok=True)
        for p in proj.programs:
            for r in p.routines:
                written.append(write_partial(proj, "Routine", r.name, str(pdir / f"Routine_{p.name}_{r.name}.L5X"), program=p.name))
    return json.dumps({"written": written})


@_tool
def lf_partial(project_dir: str, kind: str, name: str, program: str = "", output: str = "") -> str:
    """Write a partial-import L5X for one Routine/Program/Tag/DataType/AddOnInstructionDefinition."""
    proj = load_project(project_dir)
    out = output or str(Path(project_dir) / "build" / "partial" / f"{kind}_{name}.L5X")
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    return write_partial(proj, kind, name, out, program=program)


@_tool
def lf_inspect(path: str, routine: str = "") -> str:
    """Summarise a project dir or L5X. With routine='Program/Routine' returns that routine's rungs/lines."""
    p = Path(path)
    proj = load_project(p) if p.is_dir() else read_l5x(p)
    if routine:
        pname, _, rname = routine.partition("/")
        prog = proj.find_program(pname)
        r = next((x for x in prog.routines if x.name.lower() == rname.lower()), None) if prog else None
        if not r:
            return f"routine {routine} not found"
        if r.kind == "RLL":
            return "\n".join(f"{x.number}: {'// ' + x.comment + chr(10) if x.comment else ''}{x.text}" for x in r.rungs)
        return "\n".join(r.st_lines)
    return json.dumps(project_summary(proj), indent=2)


@_tool
def lf_decompile(l5x_path: str, output_dir: str) -> str:
    """Convert an L5X export (e.g. uploaded from a live controller) into an editable project directory."""
    return str(export_project_dir(read_l5x(l5x_path), output_dir))


@_tool
def lf_check_rung(text: str) -> str:
    """Syntax-check one rung of neutral ladder text, e.g. 'XIC(A)OTE(B);'."""
    try:
        parse_rung(text)
    except RungSyntaxError as e:
        return f"ERROR: {e}"
    return json.dumps({"ok": True, "instructions": instruction_names(text), "tags": operand_tags(text)})


@_tool
def lf_hmi_build(project_dir: str, output: str = "") -> str:
    """Generate a Studio 5000 View Designer import folder (ViewApplication.hmi, screens, add-on graphics) from hmi/hmi.json."""
    from .hmi.spec import load_hmi_spec
    from .hmi.viewdesigner import build_viewdesigner
    proj = load_project(project_dir)
    spec = load_hmi_spec(proj)
    if spec is None:
        return "no hmi/hmi.json in project"
    errs = [f for f in validate(proj) if f.level == "error"]
    if errs:
        return "HMI BUILD BLOCKED by validation errors:\n" + "\n".join(str(e) for e in errs)
    out = Path(output) if output else Path(project_dir) / "build" / "hmi"
    return json.dumps({"written": build_viewdesigner(proj, spec, out)})


@_tool
def lf_docs_build(path: str, output: str = "") -> str:
    """Generate the document set (I/O list, tags, routines, cause-and-effect, alarms, HMI tags, test plan)
    from a spec directory (-> docs/generated/) or from an .L5X export of an existing project (-> <stem>_docs/ or output)."""
    from .docs.generate import generate_docs
    p = Path(path)
    proj = load_project(p) if p.is_dir() else read_l5x(p)
    return json.dumps({"written": [str(x) for x in generate_docs(proj, output or None)]})


@_tool
def lf_docs_ingest(project_dir: str, file: str, title: str = "", doc_no: str = "", rev: str = "", used_for: str = "") -> str:
    """Add a given document (PDF/DOCX/XLSX/CSV/MD/image) to docs/input/, extract its text to docs/extracted/, index it."""
    from .docs.extract import ingest
    r = ingest(project_dir, file, title=title, doc_no=doc_no, rev=rev, used_for=used_for)
    return json.dumps({k: str(v) for k, v in r.items()})


@_tool
def lf_online_read(cip_path: str, tags: list[str]) -> str:
    """Read live tag values over EtherNet/IP via pycomm3 (read-only, safe)."""
    from .online import pycomm3_client as oc
    return json.dumps(oc.read_tags(cip_path, tags), default=str)


@_tool
def lf_online_tags(cip_path: str, program: str = "") -> str:
    """List tags of a live controller (controller scope, or a program's scope)."""
    from .online import pycomm3_client as oc
    return json.dumps(oc.list_tags(cip_path, program or None), default=str)


@_tool
def lf_online_write(cip_path: str, values: dict) -> str:
    """Write live tag values. BLOCKED unless LOGIXFORGE_ALLOW_ONLINE_WRITE=1 was set by a human."""
    from .online import pycomm3_client as oc
    return json.dumps(oc.write_tags(cip_path, {k: str(v) for k, v in values.items()}), default=str)


def main():
    if mcp is None:
        raise SystemExit("mcp package not installed: pip install 'mcp>=1.2'")
    mcp.run(transport=os.environ.get("LOGIXFORGE_MCP_TRANSPORT", "stdio"))


if __name__ == "__main__":
    main()
