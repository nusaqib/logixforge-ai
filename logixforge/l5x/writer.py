"""Project model -> L5X (RSLogix5000Content XML).

Produces files Studio 5000 accepts via:
  * File > Open  (full controller export, TargetType="Controller")
  * right-click > Import (partial import: Routine / Program / Tag / DataType / AddOnInstructionDefinition)

Design rules:
  * Emit only what Logix needs. Missing <Data> initialises to zero on import.
  * Rung text goes in CDATA exactly as Studio 5000's neutral text.
  * Descriptions/comments go in CDATA.
  * Element order inside <Controller> matters: DataTypes, Modules, AddOnInstructionDefinitions, Tags, Programs, Tasks.
"""
from __future__ import annotations

import datetime as _dt
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom

from ..model import AOI, ATOMIC_TYPES, DataType, Module, Program, Project, Routine, Tag, Task

_CDATA_MARK = "__LF_CDATA__"

STRUCT_MEMBERS = {  # predefined structures we can initialise in Decorated format
    "TIMER": [("PRE", "DINT"), ("ACC", "DINT"), ("EN", "BOOL"), ("TT", "BOOL"), ("DN", "BOOL")],
    "COUNTER": [("PRE", "DINT"), ("ACC", "DINT"), ("CU", "BOOL"), ("CD", "BOOL"), ("DN", "BOOL"), ("OV", "BOOL"), ("UN", "BOOL")],
}


def _radix(data_type: str):
    """Studio 5000 rejects Radix on structured tags ('Invalid display style'); only atomics get one."""
    if data_type in {"REAL", "LREAL"}:
        return "Float"
    if data_type in ATOMIC_TYPES:
        return "Decimal"
    return None


def _legacy_controller(processor_type: str) -> bool:
    """L6x/L7x-generation controllers (1756-L6x/L7x, 1769-Lxx, Emulate 5570) accept the older
    time-slice and redundancy pad attributes; L8x/5069/Emulate 5580 reject them."""
    p = processor_type.upper()
    return p.startswith(("1756-L6", "1756-L7", "1769-", "EMULATE 5570"))


def _cdata(parent: ET.Element, tag: str, text: str) -> ET.Element:
    e = ET.SubElement(parent, tag)
    e.text = f"{_CDATA_MARK}{text}{_CDATA_MARK}"
    return e


def _now() -> str:
    return _dt.datetime.now().strftime("%a %b %d %H:%M:%S %Y")


def _l5k_value(v) -> str:
    """Render a python value as L5K data text: scalars, lists -> [..], dicts -> [..] in member order."""
    if v is None:
        return "0"
    if isinstance(v, bool):
        return "1" if v else "0"
    if isinstance(v, (int, float)):
        return repr(v) if isinstance(v, float) else str(v)
    if isinstance(v, str):
        return "'" + v.replace("'", "$'") + "'"
    if isinstance(v, (list, tuple)):
        return "[" + ",".join(_l5k_value(x) for x in v) + "]"
    if isinstance(v, dict):
        return "[" + ",".join(_l5k_value(x) for x in v.values()) + "]"
    return str(v)


# ---------------------------------------------------------------------- pieces

def _data_type_el(parent: ET.Element, dt: DataType, use: str = "") -> ET.Element:
    e = ET.SubElement(parent, "DataType", Name=dt.name, Family=dt.family, Class="User")
    if use:
        e.set("Use", use)
    if dt.description:
        _cdata(e, "Description", dt.description)
    members = ET.SubElement(e, "Members")
    for m in dt.members:
        me = ET.SubElement(members, "Member", Name=m.name, DataType=m.data_type, Dimension=str(m.dimension))
        radix = m.radix or _radix(m.data_type)
        if radix:
            me.set("Radix", radix)
        me.set("Hidden", "false")
        me.set("ExternalAccess", m.external_access)
        if m.description:
            _cdata(me, "Description", m.description)
    return e


def _module_el(parent: ET.Element, m: Module) -> ET.Element:
    if m.raw_xml:
        el = ET.fromstring(m.raw_xml)
        parent.append(el)
        return el
    e = ET.SubElement(parent, "Module", Name=m.name, CatalogNumber=m.catalog_number, Vendor=str(m.vendor),
                      ProductType=str(m.product_type), ProductCode=str(m.product_code), Major=str(m.major),
                      Minor=str(m.minor), ParentModule=m.parent, ParentModPortId=str(m.parent_port_id),
                      Inhibited=str(m.inhibited).lower(), MajorFault=str(m.major_fault).lower())
    if m.description:
        _cdata(e, "Description", m.description)
    ET.SubElement(e, "EKey", State=m.ekey)
    ports = ET.SubElement(e, "Ports")
    ET.SubElement(ports, "Port", Id="1", Address=m.address, Type=m.port_type, Upstream="true")
    return e


def _tag_el(parent: ET.Element, t: Tag, use: str = "", proj=None) -> ET.Element:
    if t.alias_for:
        e = ET.SubElement(parent, "Tag", Name=t.name, TagType="Alias", Radix=t.radix or "Decimal", AliasFor=t.alias_for,
                          ExternalAccess=t.external_access)
    else:
        radix = t.radix or _radix(t.data_type)
        attrs = dict(Name=t.name, TagType="Base", DataType=t.data_type)
        if t.dimensions:
            attrs["Dimensions"] = t.dimensions
        if radix:
            attrs["Radix"] = radix
        attrs["Constant"] = str(t.constant).lower()
        attrs["ExternalAccess"] = t.external_access
        if t.usage:
            attrs["Usage"] = t.usage
        if t.produced:
            attrs["TagType"] = "Produced"
        elif t.consumed:
            attrs["TagType"] = "Consumed"
        e = ET.SubElement(parent, "Tag", **attrs)
    if use:
        e.set("Use", use)
    if t.description:
        _cdata(e, "Description", t.description)
    _alarm_conditions_el(e, t, proj)
    if t.produced:
        ET.SubElement(e, "ProduceInfo", ProduceCount=str(t.produced.get("count", 1)),
                      ProgrammaticallySend="false", UnicastPermitted="true")
    if t.consumed:
        ET.SubElement(e, "ConsumeInfo", Producer=t.consumed["producer"], RemoteTag=t.consumed["remote_tag"],
                      RPI=str(t.consumed.get("rpi", 20)))
    if t.value is not None and not t.alias_for:
        _data_el(e, t.data_type, t.dimensions, t.value, proj)
    return e


# ---------------------------------------------------------------- tag-based alarms
_ALARM_BOOL_DEFAULTS = dict(
    ProgAck="false", OperAck="false", ProgReset="false", OperReset="false", ProgSuppress="false",
    OperSuppress="false", ProgUnsuppress="false", OperUnsuppress="false", OperShelve="false",
    ProgUnshelve="false", OperUnshelve="false", ProgDisable="false", OperDisable="false", ProgEnable="false",
    OperEnable="false", AlarmCountReset="false", GroupOperExcluded="false", GroupRollupExcluded="false",
)


def _alarm_conditions_el(tag_el: ET.Element, t: Tag, proj) -> None:
    """<AlarmConditions> for tag-based alarms attached to this tag (Logix Import/Export RM014, ch. 7)."""
    if proj is None or not proj.alarms:
        return
    prog = t.scope.split(":", 1)[1] if t.scope.startswith("program:") else ""
    mine = [a for a in proj.alarms if a.tag.lower() == t.name.lower() and (a.program or "").lower() == prog.lower()]
    if not mine:
        return
    conds = ET.SubElement(tag_el, "AlarmConditions")
    for a in mine:
        attrs = dict(Name=a.name, Input=a.member, ConditionType=a.condition, Limit=repr(float(a.limit)),
                     Severity=str(a.severity), DelayOn=str(a.on_delay_ms), DelayOff=str(a.off_delay_ms),
                     ShelveDuration="0", MaxShelveDuration="0", Deadband=repr(float(a.deadband)),
                     Used=str(a.used).lower(), InFault="false", AckRequired=str(a.ack_required).lower(),
                     Latched=str(a.latched).lower())
        attrs.update(_ALARM_BOOL_DEFAULTS)
        attrs["EvaluationGroup"] = "500 millisecond"
        attrs["Expression"] = _alarm_expression(a.condition)
        if a.target_tag:
            attrs["TargetTag"] = a.target_tag
        c = ET.SubElement(conds, "AlarmCondition", **attrs)
        cfg = ET.SubElement(c, "AlarmConfig")
        msgs = ET.SubElement(cfg, "Messages")
        m = ET.SubElement(msgs, "Message", Type="CAM")
        _cdata(m, "Text", a.message or a.name).set("Lang", a.lang)
        if a.alarm_class:
            _cdata(cfg, "AlarmClass", a.alarm_class)
        if a.hmi_group:
            _cdata(cfg, "HMIGroup", a.hmi_group)


def _alarm_expression(cond: str) -> str:
    return {
        "TRIP": "Input = Limit", "HIHI": "Input > Limit", "HI": "Input > Limit", "LO": "Input < Limit",
        "LOLO": "Input < Limit", "ROC_POS": "Input >= Limit", "ROC_NEG": "Input <= Limit",
        "DEV_HI": "Input >= TargetTag + Limit", "DEV_LO": "Input <= TargetTag - Limit",
    }.get(cond, "Input = Limit")


# ---------------------------------------------------------------- initial data
def _members_of(data_type: str, proj):
    if proj is not None:
        udt = next((d for d in proj.data_types if d.name == data_type), None)
        if udt:
            return [(m.name, m.data_type, m.dimension) for m in udt.members]
    if data_type in STRUCT_MEMBERS:
        return [(n, t, 0) for n, t in STRUCT_MEMBERS[data_type]]
    return None


def _atomic_value(data_type: str, v) -> str:
    if v is None:
        return "0.0" if data_type in {"REAL", "LREAL"} else "0"
    if isinstance(v, bool):
        return "1" if v else "0"
    if data_type in {"REAL", "LREAL"}:
        return repr(float(v))
    return str(int(v)) if not isinstance(v, str) else v


def _decorated_member(parent, name: str, data_type: str, dimension: int, v, proj):
    """Emit DataValueMember / ArrayMember / StructureMember for a structure member."""
    if dimension:
        arr = ET.SubElement(parent, "ArrayMember", Name=name, DataType=data_type, Dimensions=str(dimension))
        r = _radix(data_type)
        if r:
            arr.set("Radix", r)
        vals = list(v) if isinstance(v, (list, tuple)) else [v] * dimension
        for i in range(dimension):
            el = ET.SubElement(arr, "Element", Index=f"[{i}]")
            if data_type in ATOMIC_TYPES:
                el.set("Value", _atomic_value(data_type, vals[i] if i < len(vals) else None))
            else:
                _decorated_structure(el, data_type, vals[i] if i < len(vals) else None, proj, tag="Structure")
        return
    if data_type in ATOMIC_TYPES:
        el = ET.SubElement(parent, "DataValueMember", Name=name, DataType=data_type)
        r = _radix(data_type)
        if r:
            el.set("Radix", r)
        el.set("Value", _atomic_value(data_type, v))
        return
    _decorated_structure(parent, data_type, v, proj, tag="StructureMember", name=name)


def _decorated_structure(parent, data_type: str, v, proj, tag="Structure", name=None):
    members = _members_of(data_type, proj)
    if members is None:
        return None
    st = ET.SubElement(parent, tag, DataType=data_type)
    if name:
        st.set("Name", name)
    if isinstance(v, dict):
        lookup = {k.lower(): val for k, val in v.items()}
        get = lambda i, n: lookup.get(n.lower())
    elif isinstance(v, (list, tuple)):
        get = lambda i, n: v[i] if i < len(v) else None
    else:
        get = lambda i, n: None
    for i, (mname, mtype, mdim) in enumerate(members):
        _decorated_member(st, mname, mtype, mdim, get(i, mname), proj)
    return st


def _data_el(tag_el, data_type: str, dimensions: str, value, proj):
    """Initial value: L5K for scalars, Decorated (member-named) for structures and arrays so BOOL
    packing and member order never matter."""
    if data_type in ATOMIC_TYPES and not dimensions:
        d = ET.SubElement(tag_el, "Data", Format="L5K")
        d.text = f"{_CDATA_MARK}{_l5k_value(value)}{_CDATA_MARK}"
        return
    if dimensions:
        if "," in dimensions or (data_type not in ATOMIC_TYPES and _members_of(data_type, proj) is None):
            return  # unsupported: multi-dim or unknown structure array -> Logix zero-initialises
        n = int(dimensions)
        d = ET.SubElement(tag_el, "Data", Format="Decorated")
        arr = ET.SubElement(d, "Array", DataType=data_type, Dimensions=dimensions)
        r = _radix(data_type)
        if r:
            arr.set("Radix", r)
        vals = list(value) if isinstance(value, (list, tuple)) else [value] * n
        for i in range(n):
            el = ET.SubElement(arr, "Element", Index=f"[{i}]")
            if data_type in ATOMIC_TYPES:
                el.set("Value", _atomic_value(data_type, vals[i] if i < len(vals) else None))
            else:
                _decorated_structure(el, data_type, vals[i] if i < len(vals) else None, proj)
        return
    if _members_of(data_type, proj) is None:
        return
    d = ET.SubElement(tag_el, "Data", Format="Decorated")
    _decorated_structure(d, data_type, value, proj)


def _routine_el(parent: ET.Element, r: Routine, use: str = "") -> ET.Element:
    e = ET.SubElement(parent, "Routine", Name=r.name, Type=r.kind)
    if use:
        e.set("Use", use)
    if r.description:
        _cdata(e, "Description", r.description)
    if r.kind == "RLL":
        c = ET.SubElement(e, "RLLContent")
        for i, rung in enumerate(r.rungs):
            re_ = ET.SubElement(c, "Rung", Number=str(i), Type=rung.rung_type)
            if rung.comment:
                _cdata(re_, "Comment", rung.comment)
            _cdata(re_, "Text", rung.text)
    elif r.kind == "ST":
        c = ET.SubElement(e, "STContent")
        for i, line in enumerate(r.st_lines):
            _cdata(c, "Line", line).set("Number", str(i))
    elif r.kind == "FBD" and r.fbd_sheets_xml:
        e.append(ET.fromstring(r.fbd_sheets_xml))
    return e


def _program_el(parent: ET.Element, p: Program, use: str = "", proj=None) -> ET.Element:
    attrs = dict(Name=p.name, TestEdits="false", MainRoutineName=p.main_routine, Disabled=str(p.disabled).lower(),
                 UseAsFolder="false")
    if p.fault_routine:
        attrs["FaultRoutineName"] = p.fault_routine
    if p.kind == "Safety":
        attrs["Class"] = "Safety"
    e = ET.SubElement(parent, "Program", **attrs)
    if use:
        e.set("Use", use)
    if p.description:
        _cdata(e, "Description", p.description)
    tags = ET.SubElement(e, "Tags")
    for t in p.tags:
        _tag_el(tags, t, proj=proj)
    routines = ET.SubElement(e, "Routines")
    for r in p.routines:
        _routine_el(routines, r)
    return e


def _task_el(parent: ET.Element, t: Task) -> ET.Element:
    attrs = dict(Name=t.name, Type=t.kind)
    if t.kind == "PERIODIC":
        attrs["Rate"] = str(t.rate_ms if t.rate_ms is not None else 10)
    if t.kind == "EVENT":
        attrs["EventTrigger"] = t.event_trigger or "EVENT Instruction Only"
        if t.event_tag:
            attrs["EventTag"] = t.event_tag
        attrs["EnableTimeout"] = "false"
    attrs.update(Priority=str(t.priority), Watchdog=str(t.watchdog_ms),
                 DisableUpdateOutputs=str(t.disable_update_outputs).lower(), InhibitTask=str(t.inhibit).lower())
    e = ET.SubElement(parent, "Task", **attrs)
    if t.description:
        _cdata(e, "Description", t.description)
    sp = ET.SubElement(e, "ScheduledPrograms")
    for name in t.programs:
        ET.SubElement(sp, "ScheduledProgram", Name=name)
    return e


def _aoi_el(parent: ET.Element, a: AOI, use: str = "") -> ET.Element:
    e = ET.SubElement(parent, "AddOnInstructionDefinition", Name=a.name, Class="Standard", Revision=a.revision,
                      Vendor=a.vendor, ExecutePrescan=str(a.execute_prescan).lower(),
                      ExecutePostscan=str(a.execute_postscan).lower(),
                      ExecuteEnableInFalse=str(a.execute_enable_in_false).lower(),
                      CreatedDate=_dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z"), CreatedBy="LogixForge",
                      EditedDate=_dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z"), EditedBy="LogixForge",
                      SoftwareRevision="v33.00")
    if use:
        e.set("Use", use)
    if a.description:
        _cdata(e, "Description", a.description)
    if a.revision_note:
        _cdata(e, "RevisionNote", a.revision_note)
    params = ET.SubElement(e, "Parameters")
    # Standard implicit parameters
    p = ET.SubElement(params, "Parameter", Name="EnableIn", TagType="Base", DataType="BOOL", Usage="Input",
                      Radix="Decimal", Required="false", Visible="false", ExternalAccess="Read Only")
    _cdata(p, "Description", "Enable Input - System Defined Parameter")
    p = ET.SubElement(params, "Parameter", Name="EnableOut", TagType="Base", DataType="BOOL", Usage="Output",
                      Radix="Decimal", Required="false", Visible="false", ExternalAccess="Read Only")
    _cdata(p, "Description", "Enable Output - System Defined Parameter")
    for prm in a.parameters:
        attrs = dict(Name=prm.name, TagType="Base", DataType=prm.data_type, Usage=prm.usage)
        if prm.dimension:
            attrs["Dimensions"] = str(prm.dimension)
        radix = _radix(prm.data_type)
        if radix:
            attrs["Radix"] = radix
        attrs.update(Required=str(prm.required).lower(), Visible=str(prm.visible).lower(),
                     ExternalAccess=prm.external_access)
        if prm.usage == "InOut":
            attrs.pop("ExternalAccess", None)
            attrs["Required"] = "true"
            attrs["Visible"] = "true"
        pe = ET.SubElement(params, "Parameter", **attrs)
        if prm.description:
            _cdata(pe, "Description", prm.description)
        if prm.default is not None and prm.usage != "InOut":
            d = ET.SubElement(pe, "DefaultData", Format="L5K")
            d.text = f"{_CDATA_MARK}{_l5k_value(prm.default)}{_CDATA_MARK}"
    lt = ET.SubElement(e, "LocalTags")
    for t in a.local_tags:
        attrs = dict(Name=t.name, DataType=t.data_type)
        if t.dimensions:
            attrs["Dimensions"] = t.dimensions
        radix = _radix(t.data_type)
        if radix:
            attrs["Radix"] = radix
        attrs["ExternalAccess"] = "None"
        le = ET.SubElement(lt, "LocalTag", **attrs)
        if t.description:
            _cdata(le, "Description", t.description)
        if t.value is not None and t.data_type in ATOMIC_TYPES and not t.dimensions:
            d = ET.SubElement(le, "DefaultData", Format="L5K")
            d.text = f"{_CDATA_MARK}{_l5k_value(t.value)}{_CDATA_MARK}"
    routines = ET.SubElement(e, "Routines")
    for r in a.routines:
        _routine_el(routines, r)
    return e


# ------------------------------------------------------------------- documents

def _root(target_name: str, target_type: str, contains_context: bool, software_revision: str) -> ET.Element:
    return ET.Element("RSLogix5000Content", SchemaRevision="1.0", SoftwareRevision=software_revision,
                      TargetName=target_name, TargetType=target_type, ContainsContext=str(contains_context).lower(),
                      Owner="LogixForge", ExportDate=_now(),
                      ExportOptions="References NoRawData L5KData DecoratedData ForceProtectedEncoding AllProjDocTrans")


def _controller_el(root: ET.Element, proj: Project, use: str) -> ET.Element:
    c = proj.controller
    attrs = dict(Use=use, Name=c.name)
    if use == "Target":
        attrs.update(ProcessorType=c.processor_type, MajorRev=str(c.major_rev), MinorRev=str(c.minor_rev),
                     TimeSlice=str(c.time_slice))
        if _legacy_controller(c.processor_type):
            attrs["ShareUnusedTimeSlice"] = "1"
        if c.power_loss_program:
            attrs["PowerLossProgram"] = c.power_loss_program
        if c.major_fault_program:
            attrs["MajorFaultProgram"] = c.major_fault_program
        attrs.update(ProjectCreationDate=_now(), LastModifiedDate=_now(), SFCExecutionControl="CurrentActive",
                     SFCRestartPosition="MostRecent", SFCLastScan="DontScan", ProjectSN="16#0000_0000",
                     MatchProjectToController="false", CanUseRPIFromProducer="false",
                     InhibitAutomaticFirmwareUpdate="0", PassThroughConfiguration="EnabledWithAppend",
                     DownloadProjectDocumentationAndExtendedProperties="true", DownloadProjectCustomProperties="true",
                     ReportMinorOverflow="false")
    e = ET.SubElement(root, "Controller", **attrs)
    if use == "Target":
        if c.description:
            _cdata(e, "Description", c.description)
        ri = ET.SubElement(e, "RedundancyInfo", Enabled="false", KeepTestEditsOnSwitchOver="false")
        if _legacy_controller(c.processor_type):
            ri.set("IOMemoryPadPercentage", "90")
            ri.set("DataTablePadPercentage", "50")
        ET.SubElement(e, "Security", Code="0", ChangesToDetect="16#ffff_ffff_ffff_ffff")
        ET.SubElement(e, "SafetyInfo")
    return e


def build_tree(proj: Project) -> ET.ElementTree:
    """Full controller export."""
    root = _root(proj.controller.name, "Controller", False, proj.controller.software_revision)
    ctl = _controller_el(root, proj, "Target")

    dts = ET.SubElement(ctl, "DataTypes")
    for d in proj.data_types:
        _data_type_el(dts, d)

    # The controller's own 'Local' module is created by Studio 5000 from ProcessorType; emitting one
    # collides ('Local' -> 'Local1') and fails CIP identity. Only a verbatim export (raw_xml) is passed through.
    mods = ET.SubElement(ctl, "Modules")
    for m in proj.modules:
        if m.name == "Local" and not m.raw_xml:
            continue
        _module_el(mods, m)

    aois = ET.SubElement(ctl, "AddOnInstructionDefinitions")
    for a in proj.aois:
        _aoi_el(aois, a)

    tags = ET.SubElement(ctl, "Tags")
    for t in proj.tags:
        _tag_el(tags, t, proj=proj)

    progs = ET.SubElement(ctl, "Programs")
    for p in proj.programs:
        _program_el(progs, p, proj=proj)

    tasks = ET.SubElement(ctl, "Tasks")
    for t in proj.tasks:
        _task_el(tasks, t)
    return ET.ElementTree(root)


def build_partial_tree(proj: Project, kind: str, name: str, program: str = "") -> ET.ElementTree:
    """Partial import file for one Routine / Program / Tag / DataType / AddOnInstructionDefinition."""
    sw = proj.controller.software_revision
    if kind == "DataType":
        dt = next(d for d in proj.data_types if d.name == name)
        root = _root(name, "DataType", True, sw)
        ctl = _controller_el(root, proj, "Context")
        _data_type_el(ET.SubElement(ctl, "DataTypes"), dt, use="Target")
    elif kind == "AddOnInstructionDefinition":
        a = next(x for x in proj.aois if x.name == name)
        root = _root(name, "AddOnInstructionDefinition", True, sw)
        ctl = _controller_el(root, proj, "Context")
        _aoi_el(ET.SubElement(ctl, "AddOnInstructionDefinitions"), a, use="Target")
    elif kind == "Tag":
        root = _root(name, "Tag", True, sw)
        ctl = _controller_el(root, proj, "Context")
        if program:
            p = proj.find_program(program)
            t = next(x for x in p.tags if x.name == name)
            pe = ET.SubElement(ET.SubElement(ctl, "Programs"), "Program", Use="Context", Name=p.name)
            _tag_el(ET.SubElement(pe, "Tags"), t, use="Target", proj=proj)
        else:
            t = next(x for x in proj.tags if x.name == name)
            _tag_el(ET.SubElement(ctl, "Tags"), t, use="Target", proj=proj)
    elif kind == "Program":
        p = proj.find_program(name)
        root = _root(name, "Program", True, sw)
        ctl = _controller_el(root, proj, "Context")
        _program_el(ET.SubElement(ctl, "Programs"), p, use="Target", proj=proj)
    elif kind == "Routine":
        p = proj.find_program(program)
        r = next(x for x in p.routines if x.name == name)
        root = _root(name, "Routine", True, sw)
        ctl = _controller_el(root, proj, "Context")
        pe = ET.SubElement(ET.SubElement(ctl, "Programs"), "Program", Use="Context", Name=p.name)
        _routine_el(ET.SubElement(pe, "Routines"), r, use="Target")
    else:
        raise ValueError(f"unsupported partial kind {kind}")
    return ET.ElementTree(root)


def serialize(tree: ET.ElementTree) -> str:
    raw = ET.tostring(tree.getroot(), encoding="unicode")
    pretty = minidom.parseString(raw).toprettyxml(indent="", newl="\n", encoding=None)
    # restore CDATA sections (minidom escaped our markers' contents). Done on the whole text, not per
    # line: descriptions and comments may span lines, and a per-line pairing split such a section into
    # two half-open CDATA markers and produced malformed XML.
    import html
    import re as _re
    text = _re.sub(_re.escape(_CDATA_MARK) + r"(.*?)" + _re.escape(_CDATA_MARK),
                   lambda m: "<![CDATA[" + html.unescape(m.group(1)) + "]]>", pretty, flags=_re.S)
    if not text.endswith("\n"):
        text += "\n"
    text = text.replace('<?xml version="1.0" ?>', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>', 1)
    return text


def write_l5x(proj: Project, out_path: str) -> str:
    text = serialize(build_tree(proj))
    with open(out_path, "w", encoding="utf-8", newline="\r\n") as f:
        f.write(text)
    return out_path


def write_partial(proj: Project, kind: str, name: str, out_path: str, program: str = "") -> str:
    text = serialize(build_partial_tree(proj, kind, name, program))
    with open(out_path, "w", encoding="utf-8", newline="\r\n") as f:
        f.write(text)
    return out_path


def project_summary(proj: Project) -> dict:
    return {
        "controller": proj.controller.name,
        "processor": proj.controller.processor_type,
        "data_types": [d.name for d in proj.data_types],
        "aois": [a.name for a in proj.aois],
        "modules": [m.name for m in proj.modules],
        "controller_tags": len(proj.tags),
        "programs": {p.name: {"main": p.main_routine, "tags": len(p.tags),
                              "routines": {r.name: (len(r.rungs) if r.kind == "RLL" else len(r.st_lines)) for r in p.routines}}
                     for p in proj.programs},
        "tasks": {t.name: {"type": t.kind, "rate_ms": t.rate_ms, "programs": t.programs} for t in proj.tasks},
        "alarms": [a.name for a in proj.alarms],
    }


if __name__ == "__main__":  # quick manual check
    import sys
    from ..project import load_project
    print(json.dumps(project_summary(load_project(sys.argv[1])), indent=2))
