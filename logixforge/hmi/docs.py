"""HMI documentation from the PLC spec: tag interface (docs/HMI_TAGS.md) and alarm list (docs/ALARMS.csv)."""
from __future__ import annotations

import csv
from pathlib import Path

from ..model import ATOMIC_TYPES, Project


def _direction(member: str) -> str:
    if member.startswith(("Cmd_", "Cfg_")):
        return "HMI writes"
    if member.startswith(("Sts_", "Alm_")):
        return "HMI reads"
    return "read"


def hmi_tags_markdown(proj: Project) -> str:
    lines = [f"# {proj.controller.name} - HMI tag interface", "",
             "Controller-scope tags the HMI binds to. Program-scope tags are intentionally not listed.", ""]
    for t in proj.tags:
        if t.external_access == "None":
            continue
        udt = next((d for d in proj.data_types if d.name == t.data_type), None)
        if udt:
            lines += [f"## {t.name} : {t.data_type}", "", t.description or "", "",
                      "| Member | Type | Direction | Description |", "|---|---|---|---|"]
            for m in udt.members:
                if m.data_type in ATOMIC_TYPES:
                    lines.append(f"| {t.name}.{m.name} | {m.data_type} | {_direction(m.name)} | {m.description} |")
            lines.append("")
    simple = [t for t in proj.tags if t.external_access != "None"
              and (t.data_type in ATOMIC_TYPES or t.alias_for)]
    if simple:
        lines += ["## Atomic tags", "", "| Tag | Type | Access | Description |", "|---|---|---|---|"]
        for t in simple:
            lines.append(f"| {t.name} | {t.data_type or 'alias ' + t.alias_for} | {t.external_access} | {t.description} |")
        lines.append("")
    if proj.alarms:
        lines += ["## Alarms", "", "Tag-based alarm conditions defined in the controller (shown by PanelView 5000 Alarm Summary).", "",
                  "| Alarm | Input | Condition | Severity | Class | Message |", "|---|---|---|---|---|---|"]
        for a in proj.alarms:
            lines.append(f"| {a.name} | {a.input_path} | {a.condition} | {a.severity} | {a.alarm_class} | {a.message} |")
        lines.append("")
    return "\n".join(lines)


def write_hmi_docs(proj: Project, docs_dir: str | Path) -> list[Path]:
    d = Path(docs_dir)
    d.mkdir(parents=True, exist_ok=True)
    out = [d / "HMI_TAGS.md"]
    out[0].write_text(hmi_tags_markdown(proj), encoding="utf-8")
    if proj.alarms:
        p = d / "ALARMS.csv"
        with open(p, "w", newline="", encoding="utf-8") as f:
            wr = csv.writer(f)
            wr.writerow(["Name", "Input", "Condition", "Severity", "Class", "Group", "Latched", "AckRequired", "OnDelay_ms", "Message"])
            for a in proj.alarms:
                wr.writerow([a.name, a.input_path, a.condition, a.severity, a.alarm_class, a.hmi_group, a.latched,
                             a.ack_required, a.on_delay_ms, a.message])
        out.append(p)
    return out
