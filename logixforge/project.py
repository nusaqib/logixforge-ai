"""Load a LogixForge project directory into a Project model.

Directory layout (all optional except controller.json):

    <project>/
      controller.json            {"name":..., "processor_type":..., "major_rev":...}
      modules.json               [ {module}, ... ]   (or modules/*.json, modules/*.xml raw <Module>)
      datatypes/*.json           one UDT per file
      aois/<AOI_NAME>/aoi.json   + routines/*.rll|*.st
      tags/*.json                each file is a list of controller tags
      programs/<NAME>/program.json
      programs/<NAME>/tags.json
      programs/<NAME>/routines/<ROUTINE>.rll | .st
      tasks.json                 [ {task}, ... ]
      alarms.json                [ {alarm}, ... ]   tag-based alarm conditions (see plc-alarms skill)
      hmi/hmi.json               HMI spec (see hmi-view-designer skill)

Rung files (.rll): blank-line-separated rungs. Lines starting with '//' directly
above a rung become the rung comment. A rung may span multiple lines; it ends at ';'.
First line may be '//! <routine description>'.
ST files (.st): verbatim Structured Text.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from .model import (AOI, AOIParameter, Alarm, Controller, DataType, Member, Module, Program, Project, Routine, Rung,
                    Tag, Task)


class SpecError(ValueError):
    pass


def _read_json(p: Path):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise SpecError(f"{p}: invalid JSON: {e}") from e


def _tag(d: dict, scope: str) -> Tag:
    return Tag(
        name=d["name"],
        data_type=d.get("data_type", d.get("type", "")),
        dimensions=str(d.get("dimensions", d.get("dim", "")) or ""),
        description=d.get("description", ""),
        alias_for=d.get("alias_for", ""),
        value=d.get("value"),
        constant=bool(d.get("constant", False)),
        external_access=d.get("external_access", "Read/Write"),
        radix=d.get("radix"),
        usage=d.get("usage", ""),
        produced=d.get("produced"),
        consumed=d.get("consumed"),
        scope=scope,
    )


def parse_rll_text(text: str, source: str = "") -> list[Rung]:
    """Parse a .rll file into rungs."""
    rungs: list[Rung] = []
    comment_lines: list[str] = []
    buf: list[str] = []
    for raw in text.splitlines():
        stripped = raw.strip()
        if not buf and stripped.startswith("//"):
            comment_lines.append(stripped[2:].strip())
            continue
        if not stripped:
            if buf:
                raise SpecError(f"{source}: rung not terminated with ';' before blank line: {' '.join(buf)!r}")
            continue
        buf.append(stripped)
        if stripped.endswith(";"):
            rungs.append(Rung(text=" ".join(buf), comment="\n".join(comment_lines), number=len(rungs)))
            buf, comment_lines = [], []
    if buf:
        raise SpecError(f"{source}: last rung not terminated with ';'")
    return rungs


def load_routine(path: Path) -> Routine:
    ext = path.suffix.lower()
    text = path.read_text(encoding="utf-8")
    desc = ""
    if text.startswith("//!"):
        first, _, rest = text.partition("\n")
        desc, text = first[3:].strip(), rest
    if ext == ".rll":
        return Routine(name=path.stem, kind="RLL", description=desc, rungs=parse_rll_text(text, str(path)))
    if ext == ".st":
        return Routine(name=path.stem, kind="ST", description=desc, st_lines=text.splitlines())
    if ext == ".fbd":
        return Routine(name=path.stem, kind="FBD", description=desc, fbd_sheets_xml=text)
    raise SpecError(f"unknown routine file type: {path}")


def _load_routines(dir_: Path) -> list[Routine]:
    if not dir_.is_dir():
        return []
    return [load_routine(p) for p in sorted(dir_.iterdir()) if p.suffix.lower() in {".rll", ".st", ".fbd"}]


def _tag_list(data) -> list:
    if isinstance(data, dict):
        return data.get("tags", [])
    return data


def load_project(root: "str | os.PathLike") -> Project:
    root = Path(root)
    cj = root / "controller.json"
    if not cj.exists():
        raise SpecError(f"missing {cj}")
    c = _read_json(cj)
    major = int(c.get("major_rev", 33))
    controller = Controller(
        name=c["name"],
        processor_type=c.get("processor_type", "1756-L83E"),
        major_rev=major,
        minor_rev=int(c.get("minor_rev", 11)),
        description=c.get("description", ""),
        time_slice=int(c.get("time_slice", 20)),
        software_revision=c.get("software_revision", f"{major}.00"),
        safety=bool(c.get("safety", False)),
        chassis_size=int(c.get("chassis_size", 10)),
        slot=int(c.get("slot", 0)),
        power_loss_program=c.get("power_loss_program", ""),
        major_fault_program=c.get("major_fault_program", ""),
    )
    proj = Project(controller=controller, source_dir=str(root))

    for p in sorted((root / "datatypes").glob("*.json")):
        d = _read_json(p)
        proj.data_types.append(DataType(
            name=d["name"], description=d.get("description", ""), family=d.get("family", "NoFamily"),
            members=[Member(name=m["name"], data_type=m.get("data_type", m.get("type", "")),
                            dimension=int(m.get("dimension", 0)), description=m.get("description", ""),
                            radix=m.get("radix"), external_access=m.get("external_access", "Read/Write"))
                     for m in d.get("members", [])],
        ))

    mods: list[dict] = []
    mj = root / "modules.json"
    if mj.exists():
        mods.extend(_read_json(mj))
    for p in sorted((root / "modules").glob("*.json")):
        mods.append(_read_json(p))
    for p in sorted((root / "modules").glob("*.xml")):
        mods.append({"name": p.stem, "catalog_number": "", "raw_xml": p.read_text(encoding="utf-8")})
    for m in mods:
        proj.modules.append(Module(
            name=m["name"], catalog_number=m.get("catalog_number", ""), parent=m.get("parent", "Local"),
            parent_port_id=int(m.get("parent_port_id", 1)), address=str(m.get("address", "")),
            port_type=m.get("port_type", "ICP"), vendor=int(m.get("vendor", 1)),
            product_type=int(m.get("product_type", 0)), product_code=int(m.get("product_code", 0)),
            major=int(m.get("major", 1)), minor=int(m.get("minor", 1)), inhibited=bool(m.get("inhibited", False)),
            major_fault=bool(m.get("major_fault", False)), ekey=m.get("ekey", "CompatibleModule"),
            description=m.get("description", ""), raw_xml=m.get("raw_xml", ""),
        ))

    for adir in sorted(p for p in (root / "aois").glob("*") if p.is_dir()):
        aj = adir / "aoi.json"
        if not aj.exists():
            continue
        a = _read_json(aj)
        proj.aois.append(AOI(
            name=a.get("name", adir.name), revision=a.get("revision", "1.0"), description=a.get("description", ""),
            vendor=a.get("vendor", ""), revision_note=a.get("revision_note", ""),
            execute_prescan=bool(a.get("execute_prescan", False)),
            execute_postscan=bool(a.get("execute_postscan", False)),
            execute_enable_in_false=bool(a.get("execute_enable_in_false", False)),
            parameters=[AOIParameter(name=p["name"], data_type=p.get("data_type", "BOOL"), usage=p.get("usage", "Input"),
                                     required=bool(p.get("required", False)), visible=bool(p.get("visible", True)),
                                     description=p.get("description", ""), default=p.get("default"),
                                     dimension=int(p.get("dimension", 0)),
                                     external_access=p.get("external_access", "Read/Write"))
                        for p in a.get("parameters", [])],
            local_tags=[_tag(t, "aoi") for t in a.get("local_tags", [])],
            routines=_load_routines(adir / "routines"),
        ))

    for p in sorted((root / "tags").glob("*.json")):
        proj.tags.extend(_tag(t, "controller") for t in _tag_list(_read_json(p)))

    for pdir in sorted(p for p in (root / "programs").glob("*") if p.is_dir()):
        pj = pdir / "program.json"
        d = _read_json(pj) if pj.exists() else {}
        prog = Program(
            name=d.get("name", pdir.name), main_routine=d.get("main_routine", "MainRoutine"),
            fault_routine=d.get("fault_routine", ""), description=d.get("description", ""),
            disabled=bool(d.get("disabled", False)), kind=d.get("kind", "Normal"),
        )
        tj = pdir / "tags.json"
        if tj.exists():
            prog.tags = [_tag(t, f"program:{prog.name}") for t in _tag_list(_read_json(tj))]
        prog.routines = _load_routines(pdir / "routines")
        proj.programs.append(prog)

    tj = root / "tasks.json"
    if tj.exists():
        for t in _read_json(tj):
            proj.tasks.append(Task(
                name=t["name"], kind=str(t.get("kind", t.get("type", "CONTINUOUS"))).upper(),
                rate_ms=t.get("rate_ms"), priority=int(t.get("priority", 10)),
                watchdog_ms=int(t.get("watchdog_ms", 500)), programs=list(t.get("programs", [])),
                description=t.get("description", ""), inhibit=bool(t.get("inhibit", False)),
                disable_update_outputs=bool(t.get("disable_update_outputs", False)),
                event_trigger=t.get("event_trigger", ""), event_tag=t.get("event_tag", ""),
            ))

    aj = root / "alarms.json"
    if aj.exists():
        for a in _read_json(aj):
            inp = a.get("input", a.get("tag", ""))
            tag, _, member = inp.partition(".")
            proj.alarms.append(Alarm(
                name=a["name"], tag=tag, member=("." + member) if member else "", message=a.get("message", ""),
                severity=int(a.get("severity", 500)), condition=str(a.get("condition", "TRIP")).upper(),
                limit=float(a.get("limit", 0.0)), on_delay_ms=int(a.get("on_delay_ms", 0)),
                off_delay_ms=int(a.get("off_delay_ms", 0)), deadband=float(a.get("deadband", 0.0)),
                latched=bool(a.get("latched", False)), ack_required=bool(a.get("ack_required", True)),
                alarm_class=a.get("class", a.get("alarm_class", "")), hmi_group=a.get("hmi_group", a.get("group", "")),
                program=a.get("program", ""), used=bool(a.get("used", True)), target_tag=a.get("target_tag", ""),
                lang=a.get("lang", "en-US"),
            ))
    return proj
