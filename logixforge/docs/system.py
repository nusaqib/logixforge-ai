"""System overview document (docs/generated/SYSTEM.md): what the control system consists of and how
its parts connect - controller, chassis and remote adapters with addresses, networks, HMI terminal,
external data interface, software structure and the document set. The narrative (purpose, process,
operating philosophy) belongs in SPEC.md; this file is the inventory and the architecture diagram.
"""
from __future__ import annotations

import re
from collections import defaultdict
from xml.etree import ElementTree as ET

from ..model import ATOMIC_TYPES, Module, Project
from ..rll import RungSyntaxError, parse_rung

try:
    from .hmi_nav import NavModel
except ImportError:  # pragma: no cover
    NavModel = None  # type: ignore


def _t(x) -> str:
    return str(x if x is not None else "").replace("|", "\\|").replace("\n", " ")


def _id(s: str) -> str:
    return "m_" + re.sub(r"[^A-Za-z0-9_]", "_", s)


def _mname(m: "Module") -> str:
    """Display/id name of a module; unnamed chassis modules (allowed in Studio 5000 exports) are keyed by parent and slot."""
    return m.name or f"{m.parent or 'Local'}_S{module_slot(m) or '?'}"


def _q(label: str) -> str:
    """Mermaid label text inside double quotes."""
    return str(label).replace('"', "#quot;")


def module_ports(m: Module) -> list[dict]:
    """[{id, type, address, upstream}] from the verbatim <Module> XML (falls back to the model fields)."""
    if m.raw_xml:
        try:
            el = ET.fromstring(m.raw_xml)
            ports = [{"id": p.get("Id", ""), "type": p.get("Type", ""), "address": p.get("Address", ""), "upstream": p.get("Upstream") == "true"}
                     for p in el.iter("Port")]
            if ports:
                return ports
        except ET.ParseError:
            pass
    return [{"id": "1", "type": m.port_type, "address": m.address, "upstream": True}]


def module_ip(m: Module) -> str:
    for p in module_ports(m):
        if p["type"].lower() == "ethernet" and p["address"]:
            return p["address"]
    return ""


def module_slot(m: Module) -> str:
    for p in module_ports(m):
        if p["type"].lower() != "ethernet" and p["upstream"] and p["address"]:
            return p["address"]
    return ""


def _msg_and_comms(proj: Project) -> dict[str, set[str]]:
    """Instructions that talk to other devices: MSG/GSV/SSV/produced-consumed, with where they occur."""
    found: dict[str, set[str]] = defaultdict(set)
    for p in proj.programs:
        for r in p.routines:
            where = f"{p.name}/{r.name}"
            if r.kind == "RLL":
                for rung in r.rungs:
                    try:
                        for i in parse_rung(rung.text).walk():
                            if i.name in {"MSG", "GSV", "SSV", "IOT", "PXRQ"}:
                                found[i.name].add(where)
                    except RungSyntaxError:
                        pass
            else:
                for line in r.st_lines:
                    for k in ("MSG", "GSV", "SSV", "IOT"):
                        if re.search(rf"\b{k}\s*\(", line):
                            found[k].add(where)
    return found


def system_markdown(proj: Project, header: str, nav: "NavModel | None" = None, files: list[str] | None = None,
                    index_rows: list[dict] | None = None) -> str:
    c = proj.controller
    L = [header, f"# {c.name} - system overview", "",
         "Inventory and architecture derived from the project. The purpose of the system, the process it controls and the "
         "operating philosophy are described in SPEC.md; this document says what the system is made of and how it is connected.", ""]

    # 1 identification
    L += ["## 1. Identification", "", "| Item | Value |", "|---|---|",
          f"| Controller | `{c.name}` |", f"| Processor | {c.processor_type} |", f"| Firmware / Logix version | v{c.major_rev}.{c.minor_rev:02d} (software {c.software_revision}) |",
          f"| Safety controller | {'yes' if c.safety else 'no'} |", f"| Description | {_t(c.description)} |"]
    if c.power_loss_program or c.major_fault_program:
        L.append(f"| Handler programs | power-loss `{c.power_loss_program or '-'}`, major-fault `{c.major_fault_program or '-'}` |")
    if nav:
        L.append(f"| HMI | {_t(nav.title)} on {_t(nav.device) or 'PanelView'}; home screen `{_t(nav.home.rsplit(chr(92), 1)[-1]) if nav.home else '-'}` |")
    L += [f"| Size | {len(proj.data_types)} UDTs, {len(proj.aois)} AOIs, {len(proj.modules)} modules, {len(proj.tags)} controller tags, "
          f"{len(proj.programs)} programs / {sum(len(p.routines) for p in proj.programs)} routines, {len(proj.tasks)} tasks, {len(proj.alarms)} alarms |", ""]

    # 2 architecture diagram
    mods = [m for m in proj.modules if m.name.lower() != "local"]
    by_parent: dict[str, list[Module]] = defaultdict(list)
    for m in mods:
        by_parent[m.parent].append(m)
    enet = [m for m in mods if module_ip(m)]
    L += ["## 2. Architecture", "", "```mermaid", "flowchart TB", f'  CTRL["{c.name}<br/>{c.processor_type} v{c.major_rev}"]']
    if enet or nav:
        L.append('  NET(["EtherNet/IP"])')
        L.append("  CTRL --- NET")
    if nav:
        L.append(f'  HMI["HMI {_q(nav.title)}<br/>{_q(nav.device or "PanelView")}"]')
        L.append("  NET --- HMI")
    local_children = [m for m in by_parent.get("Local", []) if not module_ip(m)]
    if local_children:
        L.append(f'  subgraph LOCAL["Local chassis ({len(local_children)} modules)"]')
        for m in local_children:
            L.append(f'    {_id(_mname(m))}["{_q(_mname(m))}<br/>{_q(m.catalog_number)} slot {module_slot(m) or "?"}"]')
        L.append("  end")
        L.append("  CTRL --- LOCAL")
    for m in enet:
        kids = by_parent.get(m.name, [])
        if kids:
            L.append(f'  subgraph {_id("rack_" + m.name)}["{_q(m.name)} - {_q(m.catalog_number)} @ {module_ip(m)} ({len(kids)} modules)"]')
            for k in kids:
                L.append(f'    {_id(_mname(k))}["{_q(_mname(k))}<br/>{_q(k.catalog_number)} slot {module_slot(k) or "?"}"]')
            L.append("  end")
            L.append(f"  NET --- {_id('rack_' + m.name)}")
        else:
            L.append(f'  {_id(m.name)}["{_q(m.name)}<br/>{_q(m.catalog_number)} @ {module_ip(m)}"]')
            L.append(f"  NET --- {_id(m.name)}")
    for m in mods:
        if m.parent not in ("Local", "") and m.parent not in {e.name for e in enet} and not module_ip(m):
            L.append(f'  {_id(m.parent)} --- {_id(_mname(m))}["{_q(_mname(m))}<br/>{_q(m.catalog_number)}"]')
    ext = [t for t in proj.tags if t.produced or t.consumed]
    if ext:
        L.append('  PEER["Other controllers<br/>produced/consumed tags"]')
        L.append("  NET --- PEER")
    L += ["```", ""]

    # 3 hardware inventory
    L += ["## 3. Hardware inventory", ""]
    if mods:
        L += ["| Module | Catalog | Parent | Slot | IP address | Rev | Description |", "|---|---|---|---|---|---|---|"]
        for m in sorted(mods, key=lambda x: (x.parent != "Local", x.parent, module_slot(x).zfill(3), x.name)):
            L.append(f"| {m.name} | {m.catalog_number} | {m.parent} | {module_slot(m)} | {module_ip(m)} | {m.major}.{m.minor} | {_t(m.description)} |")
        L.append("")
        cats = defaultdict(int)
        for m in mods:
            cats[m.catalog_number] += 1
        L += ["Count by catalog number: " + ", ".join(f"{k} x{v}" for k, v in sorted(cats.items(), key=lambda kv: -kv[1])) + ".", ""]
    else:
        L += ["(no I/O modules in the project; add Studio 5000 module exports to `modules/`)", ""]

    # 4 networks and interfaces
    L += ["## 4. Networks and communication interfaces", ""]
    if enet:
        L += ["| Device | Catalog | IP address | Role |", "|---|---|---|---|"]
        for m in enet:
            role = "remote I/O adapter" if by_parent.get(m.name) else "EtherNet/IP device"
            L.append(f"| {m.name} | {m.catalog_number} | {module_ip(m)} | {role} |")
        L.append("")
    comms = _msg_and_comms(proj)
    if comms:
        L += ["| Instruction | Used in |", "|---|---|"] + [f"| {k} | {_t(', '.join(sorted(v)))} |" for k, v in sorted(comms.items())] + [""]
    if ext:
        L += ["Produced / consumed tags:", ""] + [f"- `{t.name}` {'produced' if t.produced else 'consumed'} ({t.data_type})" for t in ext] + [""]
    if not enet and not comms and not ext:
        L += ["No remote devices, message instructions or produced/consumed tags found.", ""]

    # 5 software structure
    L += ["## 5. Control software", "", "| Task | Type | Rate | Programs (routines) |", "|---|---|---|---|"]
    for t in proj.tasks:
        progs = ", ".join(f"{pn} ({len(proj.find_program(pn).routines) if proj.find_program(pn) else '?'})" for pn in t.programs)
        L.append(f"| {t.name} | {t.kind} | {str(t.rate_ms) + ' ms' if t.rate_ms else '-'} | {_t(progs)} |")
    L.append("")
    if proj.aois:
        vendor = [a.name for a in proj.aois if a.vendor]
        site = [a.name for a in proj.aois if not a.vendor]
        L.append(f"Add-On Instructions: {len(proj.aois)} ({len(site)} project/site, {len(vendor)} vendor). Details in TAGS.md and ROUTINES.md.")
    if proj.data_types:
        L.append(f"User-defined data types: {', '.join(d.name for d in proj.data_types)}.")
    L.append("")

    # 6 operator interface
    L += ["## 6. Operator interface", ""]
    if nav:
        user = [s for s in nav.screens if s.kind == "user"]
        L.append(f"HMI project `{nav.title}` on {nav.device or 'PanelView'}: {len(user)} screens in {len(nav.folders)} folders, "
                 f"{len(nav.shortcuts)} menu shortcuts, {len(nav.aogs)} Add-On Graphics. Screen hierarchy and navigation in HMI_NAVIGATION.md; tag interface in HMI_TAGS.md.")
    else:
        L.append("No HMI definition in the project (add `hmi/hmi.json` or pass a View Designer export with `--hmi`). Tag interface in HMI_TAGS.md.")
    L.append(f"Controller alarms: {len(proj.alarms)} tag-based alarm conditions (ALARMS.csv)." if proj.alarms else "Controller alarms: none defined in the controller (alarming is external or instruction-based).")
    L.append("")

    # 7 external data interface
    L += ["## 7. External data interface (controller-scope tags)", "",
          "Tags other systems (HMI, SCADA/EPICS, peer controllers) can address. Program-scope tags are not externally addressable by most clients.", "",
          "| Tag | Type | Dim | External access | Description |", "|---|---|---|---|---|"]
    for t in proj.tags:
        L.append(f"| {t.name} | {t.data_type or 'alias ' + t.alias_for} | {t.dimensions} | {t.external_access} | {_t(t.description)} |")
    L.append("")

    # 8 document set
    L += ["## 8. Document set", ""]
    if index_rows:
        L += ["Given documents (docs/INDEX.md):", "", "| Document | Number | Rev | Used for |", "|---|---|---|---|"]
        L += [f"| {_t(r.get('Title'))} | {_t(r.get('Document no.'))} | {_t(r.get('Rev'))} | {_t(r.get('Used for'))} |" for r in index_rows] + [""]
    L += ["Generated documents:", "", "| File | Content |", "|---|---|"]
    desc = {"SPEC.md": "functional description (hand-written)", "SYSTEM.md": "this overview", "IO_LIST.md": "modules and I/O points",
            "TAGS.md": "UDTs, AOIs, tags", "ROUTINES.md": "task/program/routine map", "INTERLOCKS.md": "cause and effect from the logic",
            "ALARMS.csv": "alarm list", "HMI_TAGS.md": "HMI tag interface", "HMI_NAVIGATION.md": "HMI screen hierarchy and navigation",
            "TEST_PLAN.md": "test plan skeleton", "IO_LIST.csv": "I/O points (spreadsheet)", "README.md": "index"}
    for f in (files or list(desc)):
        if f in desc:
            L.append(f"| {f} | {desc[f]} |")
    L.append("")
    return "\n".join(L)
