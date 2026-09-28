"""HMI spec (<project>/hmi/hmi.json) and faceplate contracts derived from UDTs.

hmi.json
{
  "target": "view-designer",
  "project_name": "ConveyorDemo_HMI",
  "controller_ref": "LGX",                       # name of the controller reference in View Designer
  "terminal": { "catalog": "2715P-T10CD", "width": 1280, "height": 800 },
  "home_screen": "Overview",
  "screens": [
    { "name": "Overview", "title": "Conveyor 01", "columns": 3,
      "widgets": [
        { "type": "faceplate", "tag": "HMI_Conveyor01", "label": "Conveyor 01" },
        { "type": "indicator", "tag": "I_ESTOP_OK", "label": "E-Stop", "on_text": "OK", "off_text": "ACTIVE",
          "on_color": "#2ecc71", "off_color": "#e74c3c" },
        { "type": "numeric", "tag": "HMI_Conveyor01.Sts_RunHours", "label": "Run hours", "decimals": 1, "units": "h" },
        { "type": "numeric_input", "tag": "HMI_Conveyor01.Cfg_FaultDelay_ms", "label": "Fault delay", "units": "ms",
          "min": 0, "max": 60000 },
        { "type": "button", "text": "Start", "tag": "HMI_Conveyor01.Cmd_Start", "action": "set1" },
        { "type": "nav_button", "text": "Alarms", "screen": "Navigation Menu\\AlarmSummary" },
        { "type": "bargraph", "tag": "AI_Level", "label": "Level", "min": 0, "max": 100 },
        { "type": "text", "text": "Free text" }
      ] }
  ],
  "faceplates": { "UDT_Motor": { "rows": [ ... explicit rows, optional ... ] } }
}

Faceplate rows default from UDT member prefixes:
  Cmd_* BOOL -> button (set1)   Sts_* BOOL -> indicator (green)   Alm_*/*Fault* BOOL -> indicator (red)
  Cfg_* numeric -> numeric_input   other numeric -> numeric display   REAL -> 1 decimal
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from ..model import ATOMIC_TYPES, DataType, Project

TERMINALS = {  # catalog -> (width, height)
    "2715P-T7WD": (800, 480), "2715P-T9WD": (800, 480), "2715P-T10CD": (1280, 800), "2715P-T12WD": (1280, 800),
    "2715P-T15CD": (1024, 768), "2715P-T19CD": (1280, 1024), "2715P-B7CD": (640, 480),
    "2715-T7CD": (800, 480), "2715-T10CD": (1280, 800), "2715-T12WD": (1280, 800), "2715-T15CD": (1024, 768), "2715-T19CD": (1280, 1024),
}
BANNER_HEIGHT_800 = 51.5   # default banner height on an 800 px wide terminal (scales with width)


@dataclass
class Widget:
    type: str
    tag: str = ""
    label: str = ""
    text: str = ""
    screen: str = ""
    action: str = "set1"          # button: set1 | set0 | toggle
    units: str = ""
    decimals: int | None = None
    min: float | None = None
    max: float | None = None
    on_text: str = "ON"
    off_text: str = "OFF"
    on_color: str = "#2ecc71"
    off_color: str = "#7f8c8d"
    span: int = 1                 # grid columns
    udt: str = ""                 # faceplate: UDT name (resolved from tag if omitted)
    member: str = ""              # faceplate rows: member name


@dataclass
class Screen:
    name: str
    title: str = ""
    columns: int = 3
    widgets: list[Widget] = field(default_factory=list)
    fill_color: str = "#f4f6f8"
    in_menu: bool = True


@dataclass
class Faceplate:
    udt: str
    rows: list[Widget] = field(default_factory=list)
    title: str = ""


@dataclass
class HmiSpec:
    target: str = "view-designer"
    project_name: str = ""
    controller_ref: str = "LGX"
    catalog: str = "2715P-T10CD"
    width: int = 1280
    height: int = 800
    screen_height: float = 0.0
    home_screen: str = ""
    screens: list[Screen] = field(default_factory=list)
    faceplates: dict[str, Faceplate] = field(default_factory=dict)
    lang: str = "en-US"

    def screen(self, name: str) -> Screen | None:
        return next((s for s in self.screens if s.name.lower() == name.lower()), None)


def _widget(d: dict) -> Widget:
    w = Widget(type=d["type"])
    for k, v in d.items():
        if k == "type":
            continue
        key = {"class": "alarm_class"}.get(k, k)
        if hasattr(w, key):
            setattr(w, key, v)
    return w


def load_hmi_spec(proj: Project, path: str | Path | None = None) -> HmiSpec | None:
    p = Path(path) if path else Path(proj.source_dir) / "hmi" / "hmi.json"
    if not p.is_file():
        return None
    d = json.loads(p.read_text(encoding="utf-8"))
    term = d.get("terminal", {})
    catalog = term.get("catalog", "2715P-T10CD")
    w, h = TERMINALS.get(catalog, (1280, 800))
    spec = HmiSpec(
        target=d.get("target", "view-designer"), project_name=d.get("project_name", f"{proj.controller.name}_HMI"),
        controller_ref=d.get("controller_ref", "LGX"), catalog=catalog, width=int(term.get("width", w)),
        height=int(term.get("height", h)), home_screen=d.get("home_screen", ""), lang=d.get("lang", "en-US"),
    )
    spec.screen_height = float(term.get("screen_height", 0) or (spec.height - BANNER_HEIGHT_800 * spec.width / 800))
    for s in d.get("screens", []):
        spec.screens.append(Screen(name=s["name"], title=s.get("title", s["name"]), columns=int(s.get("columns", 3)),
                                   widgets=[_widget(x) for x in s.get("widgets", [])],
                                   fill_color=s.get("fill_color", "#f4f6f8"), in_menu=bool(s.get("in_menu", True))))
    if not spec.home_screen and spec.screens:
        spec.home_screen = spec.screens[0].name
    for udt, f in d.get("faceplates", {}).items():
        spec.faceplates[udt] = Faceplate(udt=udt, title=f.get("title", ""), rows=[_widget(x) for x in f.get("rows", [])])
    # auto-derive faceplates for every UDT used by a faceplate widget
    for s in spec.screens:
        for wdg in s.widgets:
            if wdg.type == "faceplate":
                udt = wdg.udt or _tag_type(proj, wdg.tag) or ""
                wdg.udt = udt
                if udt and udt not in spec.faceplates:
                    dt = next((x for x in proj.data_types if x.name == udt), None)
                    if dt:
                        spec.faceplates[udt] = derive_faceplate(dt)
    return spec


def _tag_type(proj: Project, tag: str) -> str | None:
    base = tag.split(".")[0].split("[")[0]
    t = next((x for x in proj.tags if x.name.lower() == base.lower()), None)
    return t.data_type if t else None


def _pretty(member: str) -> str:
    s = re.sub(r"^(Cmd|Sts|Cfg|Alm|Sim|Int)_", "", member)
    s = re.sub(r"_(ms|s|min|h|degC|bar|pct|mm|rpm|mps)$", "", s)
    return s.replace("_", " ")


def _units(member: str) -> str:
    m = re.search(r"_(ms|s|min|h|degC|bar|pct|mm|rpm|mps)$", member)
    return {"pct": "%", "degC": "°C", "mps": "m/s"}.get(m.group(1), m.group(1)) if m else ""


def derive_faceplate(dt: DataType) -> Faceplate:
    rows: list[Widget] = []
    for m in dt.members:
        if m.dimension or m.data_type not in ATOMIC_TYPES:
            continue
        name = m.name
        if m.data_type == "BOOL":
            if name.startswith("Cmd_"):
                rows.append(Widget(type="button", member=name, text=_pretty(name), action="set1"))
            elif name.startswith("Alm_") or "Fault" in name or "Alarm" in name:
                rows.append(Widget(type="indicator", member=name, label=_pretty(name), on_color="#e74c3c",
                                   off_color="#7f8c8d", on_text="FAULT", off_text="OK"))
            elif name.startswith(("Sts_", "Sim_")):
                rows.append(Widget(type="indicator", member=name, label=_pretty(name), on_color="#2ecc71",
                                   off_color="#7f8c8d", on_text="ON", off_text="OFF"))
        else:
            dec = 1 if m.data_type in {"REAL", "LREAL"} else 0
            if name.startswith("Cfg_"):
                rows.append(Widget(type="numeric_input", member=name, label=_pretty(name), units=_units(name), decimals=dec))
            elif not name.startswith("Int_"):
                rows.append(Widget(type="numeric", member=name, label=_pretty(name), units=_units(name), decimals=dec))
    return Faceplate(udt=dt.name, rows=rows, title=dt.description or dt.name)


# ---------------------------------------------------------------- validation
def hmi_findings(proj: Project, spec: HmiSpec):
    out = []
    names = set()
    if not spec.screens:
        out.append(("error", "HMI_NO_SCREENS", "hmi", "hmi.json defines no screens"))
    if spec.home_screen and spec.screen(spec.home_screen) is None:
        out.append(("error", "HMI_HOME", "hmi", f"home_screen {spec.home_screen!r} is not a defined screen"))
    if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", spec.controller_ref):
        out.append(("error", "HMI_CTRLREF", "hmi", "controller_ref must be an identifier (letters, digits, underscore)"))
    ctl_tags = {t.name.lower(): t for t in proj.tags}
    for s in spec.screens:
        w = f"hmi screen {s.name}"
        if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", s.name) or len(s.name) > 40:
            out.append(("error", "HMI_NAME", w, "screen names: letters/digits/underscore, max 40 chars"))
        if s.name.lower() in names:
            out.append(("error", "HMI_DUP", w, "duplicate screen name"))
        names.add(s.name.lower())
        for i, wd in enumerate(s.widgets):
            ww = f"{w} widget {i} ({wd.type})"
            if wd.type not in {"text", "indicator", "numeric", "numeric_input", "button", "nav_button", "bargraph", "faceplate"}:
                out.append(("error", "HMI_WIDGET", ww, f"unknown widget type {wd.type!r}"))
                continue
            if wd.type == "nav_button":
                if not wd.screen:
                    out.append(("error", "HMI_NAV", ww, "nav_button needs 'screen'"))
                elif not wd.screen.startswith(("Navigation Menu\\", "Predefined Screens\\", "User-Defined Screens\\")) \
                        and spec.screen(wd.screen) is None:
                    out.append(("error", "HMI_NAV", ww, f"target screen {wd.screen!r} not defined"))
                continue
            if wd.type == "text":
                continue
            if not wd.tag:
                out.append(("error", "HMI_TAG", ww, "widget needs 'tag'"))
                continue
            base = wd.tag.split(".")[0].split("[")[0]
            if base.lower().startswith("program:"):
                out.append(("warning", "HMI_SCOPE", ww, "program-scope binding; move the tag to controller scope for HMI"))
                continue
            t = ctl_tags.get(base.lower())
            if t is None:
                out.append(("error", "HMI_TAG", ww, f"tag {base!r} is not a controller-scope tag"))
                continue
            if wd.type == "faceplate":
                if wd.udt not in spec.faceplates:
                    out.append(("error", "HMI_FACEPLATE", ww, f"no faceplate for type {t.data_type!r} (tag {wd.tag})"))
                continue
            leaf = _leaf_type(proj, t.data_type or "BOOL", wd.tag[len(base):])
            if leaf is None:
                out.append(("error", "HMI_MEMBER", ww, f"member path {wd.tag!r} does not exist"))
            elif wd.type in {"indicator", "button"} and leaf and leaf != "BOOL":
                out.append(("error", "HMI_TYPE", ww, f"{wd.type} needs a BOOL, got {leaf}"))
            elif wd.type in {"numeric", "numeric_input", "bargraph"} and leaf and leaf not in ATOMIC_TYPES - {"BOOL"}:
                out.append(("error", "HMI_TYPE", ww, f"{wd.type} needs a numeric tag, got {leaf}"))
            if wd.type in {"button", "numeric_input"} and t.constant:
                out.append(("error", "HMI_CONST", ww, "HMI writes to a constant tag"))
            if wd.type in {"button", "numeric_input"} and t.external_access != "Read/Write":
                out.append(("error", "HMI_ACCESS", ww, f"tag ExternalAccess is {t.external_access}; HMI cannot write"))
            if t.external_access == "None":
                out.append(("error", "HMI_ACCESS", ww, "tag ExternalAccess is None; HMI cannot read it"))
    return out


def _leaf_type(proj: Project, data_type: str, member_path: str) -> str | None:
    cur = data_type
    for part in [m for m in member_path.split(".") if m]:
        part = part.split("[")[0]
        udt = next((d for d in proj.data_types if d.name == cur), None)
        if udt is None:
            return "" if cur not in ATOMIC_TYPES else None
        m = next((x for x in udt.members if x.name.lower() == part.lower()), None)
        if m is None:
            return None
        cur = m.data_type
    return cur
