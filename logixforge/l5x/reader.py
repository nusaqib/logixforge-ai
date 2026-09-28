"""L5X -> Project model (subset). Used for inspect / review / diff / round-trip of exports
from Studio 5000, including exports of live controllers (Upload -> Save As .L5X).
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from ..model import (AOI, AOIParameter, Alarm, Controller, DataType, Member, Module, Program, Project, Routine, Rung,
                     Tag, Task)


def _text(el: ET.Element | None, tag: str) -> str:
    if el is None:
        return ""
    c = el.find(tag)
    return (c.text or "").strip() if c is not None else ""


def _tag_from_el(e: ET.Element, scope: str) -> Tag:
    t = Tag(name=e.get("Name", ""), data_type=e.get("DataType", ""), dimensions=e.get("Dimensions", ""),
            description=_text(e, "Description"), alias_for=e.get("AliasFor", ""),
            constant=e.get("Constant", "false") == "true", external_access=e.get("ExternalAccess", "Read/Write"),
            radix=e.get("Radix"), usage=e.get("Usage", ""), scope=scope)
    d = e.find("Data[@Format='L5K']")
    if d is not None and d.text:
        t.value = d.text.strip()
    if e.get("TagType") == "Produced":
        pi = e.find("ProduceInfo")
        t.produced = {"count": int(pi.get("ProduceCount", 1))} if pi is not None else {"count": 1}
    if e.get("TagType") == "Consumed":
        ci = e.find("ConsumeInfo")
        if ci is not None:
            t.consumed = {"producer": ci.get("Producer"), "remote_tag": ci.get("RemoteTag"), "rpi": ci.get("RPI")}
    return t


def _routine_from_el(e: ET.Element) -> Routine:
    r = Routine(name=e.get("Name", ""), kind=e.get("Type", "RLL"), description=_text(e, "Description"))
    if r.kind == "RLL":
        for i, rung in enumerate(e.findall("RLLContent/Rung")):
            r.rungs.append(Rung(text=_text(rung, "Text"), comment=_text(rung, "Comment"),
                                number=int(rung.get("Number", i)), rung_type=rung.get("Type", "N")))
    elif r.kind == "ST":
        r.st_lines = [(l.text or "") for l in e.findall("STContent/Line")]
    elif r.kind == "FBD":
        c = e.find("FBDContent")
        if c is not None:
            r.fbd_sheets_xml = ET.tostring(c, encoding="unicode")
    return r


def _alarms_from_tag(tag_el: ET.Element, program: str) -> list[Alarm]:
    out = []
    for c in tag_el.findall("AlarmConditions/AlarmCondition"):
        cfg = c.find("AlarmConfig")
        msg = cfg.find("Messages/Message/Text") if cfg is not None else None
        out.append(Alarm(
            name=c.get("Name", ""), tag=tag_el.get("Name", ""), member=c.get("Input", ""),
            message=(msg.text or "").strip() if msg is not None else "", severity=int(c.get("Severity", 500) or 500),
            condition=c.get("ConditionType", "TRIP"), limit=float(c.get("Limit", 0) or 0),
            on_delay_ms=int(c.get("DelayOn", 0) or 0), off_delay_ms=int(c.get("DelayOff", 0) or 0),
            deadband=float(c.get("Deadband", 0) or 0), latched=c.get("Latched") == "true",
            ack_required=c.get("AckRequired", "true") == "true", alarm_class=_text(cfg, "AlarmClass"),
            hmi_group=_text(cfg, "HMIGroup"), program=program, used=c.get("Used", "true") == "true",
            target_tag=c.get("TargetTag", ""), lang=msg.get("Lang", "en-US") if msg is not None else "en-US",
        ))
    return out


def read_l5x(path: str | Path) -> Project:
    tree = ET.parse(path)
    root = tree.getroot()
    ctl = root.find("Controller")
    if ctl is None:
        raise ValueError("no <Controller> element")
    c = Controller(name=ctl.get("Name", root.get("TargetName", "")), processor_type=ctl.get("ProcessorType", ""),
                   major_rev=int(ctl.get("MajorRev", 0) or 0), minor_rev=int(ctl.get("MinorRev", 0) or 0),
                   description=_text(ctl, "Description"), software_revision=root.get("SoftwareRevision", ""),
                   power_loss_program=ctl.get("PowerLossProgram", ""), major_fault_program=ctl.get("MajorFaultProgram", ""))
    proj = Project(controller=c, source_dir=str(path))

    for d in ctl.findall("DataTypes/DataType"):
        proj.data_types.append(DataType(
            name=d.get("Name", ""), description=_text(d, "Description"), family=d.get("Family", "NoFamily"),
            members=[Member(name=m.get("Name", ""), data_type=("BOOL" if m.get("DataType") == "BIT" else m.get("DataType", "")),
                            dimension=int(m.get("Dimension", 0)),
                            description=_text(m, "Description"), radix=m.get("Radix"),
                            external_access=m.get("ExternalAccess", "Read/Write"))
                     for m in d.findall("Members/Member") if m.get("Hidden", "false") != "true"],
        ))

    for m in ctl.findall("Modules/Module"):
        port = m.find("Ports/Port")
        proj.modules.append(Module(
            name=m.get("Name", ""), catalog_number=m.get("CatalogNumber", ""), parent=m.get("ParentModule", ""),
            parent_port_id=int(m.get("ParentModPortId", 1) or 1), address=port.get("Address", "") if port is not None else "",
            port_type=port.get("Type", "") if port is not None else "", vendor=int(m.get("Vendor", 0) or 0),
            product_type=int(m.get("ProductType", 0) or 0), product_code=int(m.get("ProductCode", 0) or 0),
            major=int(m.get("Major", 0) or 0), minor=int(m.get("Minor", 0) or 0),
            inhibited=m.get("Inhibited") == "true", major_fault=m.get("MajorFault") == "true",
            description=_text(m, "Description"), raw_xml=ET.tostring(m, encoding="unicode"),
        ))

    for a in ctl.findall("AddOnInstructionDefinitions/AddOnInstructionDefinition"):
        aoi = AOI(name=a.get("Name", ""), revision=a.get("Revision", ""), description=_text(a, "Description"),
                  vendor=a.get("Vendor", ""), revision_note=_text(a, "RevisionNote"),
                  execute_prescan=a.get("ExecutePrescan") == "true", execute_postscan=a.get("ExecutePostscan") == "true",
                  execute_enable_in_false=a.get("ExecuteEnableInFalse") == "true")
        for p in a.findall("Parameters/Parameter"):
            if p.get("Name") in {"EnableIn", "EnableOut"}:
                continue
            dd = p.find("DefaultData[@Format='L5K']")
            aoi.parameters.append(AOIParameter(
                name=p.get("Name", ""), data_type=p.get("DataType", ""), usage=p.get("Usage", "Input"),
                required=p.get("Required") == "true", visible=p.get("Visible") == "true",
                description=_text(p, "Description"), default=(dd.text or "").strip() if dd is not None else None,
                dimension=int(p.get("Dimensions", 0) or 0), external_access=p.get("ExternalAccess", "Read/Write")))
        for lt in a.findall("LocalTags/LocalTag"):
            aoi.local_tags.append(Tag(name=lt.get("Name", ""), data_type=lt.get("DataType", ""),
                                      dimensions=lt.get("Dimensions", ""), description=_text(lt, "Description"), scope="aoi"))
        aoi.routines = [_routine_from_el(r) for r in a.findall("Routines/Routine")]
        proj.aois.append(aoi)

    proj.tags = [_tag_from_el(t, "controller") for t in ctl.findall("Tags/Tag")]
    for t in ctl.findall("Tags/Tag"):
        proj.alarms.extend(_alarms_from_tag(t, ""))

    for p in ctl.findall("Programs/Program"):
        prog = Program(name=p.get("Name", ""), main_routine=p.get("MainRoutineName", ""),
                       fault_routine=p.get("FaultRoutineName", ""), description=_text(p, "Description"),
                       disabled=p.get("Disabled") == "true", kind="Safety" if p.get("Class") == "Safety" else "Normal")
        prog.tags = [_tag_from_el(t, f"program:{prog.name}") for t in p.findall("Tags/Tag")]
        for t in p.findall("Tags/Tag"):
            proj.alarms.extend(_alarms_from_tag(t, prog.name))
        prog.routines = [_routine_from_el(r) for r in p.findall("Routines/Routine")]
        proj.programs.append(prog)

    for t in ctl.findall("Tasks/Task"):
        proj.tasks.append(Task(
            name=t.get("Name", ""), kind=t.get("Type", "CONTINUOUS").upper(),
            rate_ms=float(t.get("Rate")) if t.get("Rate") else None, priority=int(t.get("Priority", 10) or 10),
            watchdog_ms=int(float(t.get("Watchdog", 500) or 500)),
            programs=[sp.get("Name", "") for sp in t.findall("ScheduledPrograms/ScheduledProgram")],
            description=_text(t, "Description"), inhibit=t.get("InhibitTask") == "true",
            disable_update_outputs=t.get("DisableUpdateOutputs") == "true",
            event_trigger=t.get("EventTrigger", ""), event_tag=t.get("EventTag", ""),
        ))
    return proj


def export_project_dir(proj: Project, out_dir: str | Path) -> Path:
    """Write a Project back out as a LogixForge project directory (L5X -> spec round-trip)."""
    import json
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    c = proj.controller
    (out / "controller.json").write_text(json.dumps({
        "name": c.name, "processor_type": c.processor_type, "major_rev": c.major_rev, "minor_rev": c.minor_rev,
        "description": c.description, "software_revision": c.software_revision,
        **({"power_loss_program": c.power_loss_program} if c.power_loss_program else {}),
        **({"major_fault_program": c.major_fault_program} if c.major_fault_program else {})}, indent=2), encoding="utf-8")
    (out / "datatypes").mkdir(exist_ok=True)
    for d in proj.data_types:
        (out / "datatypes" / f"{d.name}.json").write_text(json.dumps({
            "name": d.name, "description": d.description, "family": d.family,
            "members": [{"name": m.name, "data_type": m.data_type, "dimension": m.dimension,
                         "description": m.description} for m in d.members]}, indent=2), encoding="utf-8")
    if proj.modules:
        (out / "modules").mkdir(exist_ok=True)
        for m in proj.modules:
            if m.name == "Local":
                continue
            (out / "modules" / f"{m.name}.xml").write_text(m.raw_xml, encoding="utf-8")
    (out / "tags").mkdir(exist_ok=True)
    (out / "tags" / "controller.json").write_text(json.dumps([_tag_dict(t) for t in proj.tags], indent=2), encoding="utf-8")
    for a in proj.aois:
        ad = out / "aois" / a.name
        (ad / "routines").mkdir(parents=True, exist_ok=True)
        (ad / "aoi.json").write_text(json.dumps({
            "name": a.name, "revision": a.revision, "description": a.description, "vendor": a.vendor,
            "revision_note": a.revision_note, "execute_prescan": a.execute_prescan,
            "execute_postscan": a.execute_postscan, "execute_enable_in_false": a.execute_enable_in_false,
            "parameters": [{"name": p.name, "data_type": p.data_type, "usage": p.usage, "required": p.required,
                            "visible": p.visible, "description": p.description, "default": p.default,
                            "dimension": p.dimension} for p in a.parameters],
            "local_tags": [_tag_dict(t) for t in a.local_tags]}, indent=2), encoding="utf-8")
        for r in a.routines:
            _write_routine(ad / "routines", r)
    for p in proj.programs:
        pd = out / "programs" / p.name
        (pd / "routines").mkdir(parents=True, exist_ok=True)
        (pd / "program.json").write_text(json.dumps({
            "name": p.name, "main_routine": p.main_routine, "fault_routine": p.fault_routine,
            "description": p.description, "disabled": p.disabled, "kind": p.kind}, indent=2), encoding="utf-8")
        (pd / "tags.json").write_text(json.dumps([_tag_dict(t) for t in p.tags], indent=2), encoding="utf-8")
        for r in p.routines:
            _write_routine(pd / "routines", r)
    if proj.alarms:
        (out / "alarms.json").write_text(json.dumps([{
            "name": a.name, "input": a.input_path, "message": a.message, "severity": a.severity,
            "condition": a.condition, "limit": a.limit, "on_delay_ms": a.on_delay_ms, "off_delay_ms": a.off_delay_ms,
            "latched": a.latched, "ack_required": a.ack_required, "class": a.alarm_class, "hmi_group": a.hmi_group,
            **({"program": a.program} if a.program else {})} for a in proj.alarms], indent=2), encoding="utf-8")
    (out / "tasks.json").write_text(json.dumps([{
        "name": t.name, "kind": t.kind, "rate_ms": t.rate_ms, "priority": t.priority, "watchdog_ms": t.watchdog_ms,
        "programs": t.programs, "description": t.description} for t in proj.tasks], indent=2), encoding="utf-8")
    return out


def _tag_dict(t: Tag) -> dict:
    d = {"name": t.name}
    if t.alias_for:
        d["alias_for"] = t.alias_for
    else:
        d["data_type"] = t.data_type
        if t.dimensions:
            d["dimensions"] = t.dimensions
    if t.description:
        d["description"] = t.description
    if t.constant:
        d["constant"] = True
    if t.usage:
        d["usage"] = t.usage
    if t.produced:
        d["produced"] = t.produced
    if t.consumed:
        d["consumed"] = t.consumed
    return d


def _write_routine(dir_: Path, r: Routine) -> None:
    if r.kind == "RLL":
        parts = []
        if r.description:
            parts.append(f"//! {r.description}")
        for rung in r.rungs:
            if rung.comment:
                parts.extend("// " + l for l in rung.comment.splitlines())
            parts.append(rung.text)
            parts.append("")
        (dir_ / f"{r.name}.rll").write_text("\n".join(parts), encoding="utf-8")
    elif r.kind == "ST":
        head = f"//! {r.description}\n" if r.description else ""
        (dir_ / f"{r.name}.st").write_text(head + "\n".join(r.st_lines), encoding="utf-8")
    elif r.kind == "FBD":
        (dir_ / f"{r.name}.fbd").write_text(r.fbd_sheets_xml, encoding="utf-8")
