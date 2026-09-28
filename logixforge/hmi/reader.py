"""Read a Studio 5000 View Designer project export (File > Export Project folder of .hmi text files).

Enough structure for documentation and review: screens with their folder path, navigation edges
(BehaviorNavigateToScreen / NavigateTo / popups), shortcuts (Navigation Menu), tag bindings, Add-On
Graphic usage and per-screen security. It does not parse element geometry.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

NAV_RE = re.compile(r'(?:screenName|NavigateTo|TargetScreenName)\s*:=\s*"([^"]+)"')
POPUP_RE = re.compile(r'PopupName\s*:=\s*"([^"]+)"')
BIND_RE = re.compile(r'::([A-Za-z_][A-Za-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_.:\[\]]*)')   # ::ctrl.Tag.Member, also inside expressions
ROLE_RE = re.compile(r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:=\s*RoleAccess\.([A-Za-z]+);', re.M)
HEAD_RE = re.compile(r'^(Screen|Shortcut|AddOnGraphic|ViewFolder|ViewProject|Controller|Banner)\s*([A-Za-z_][A-Za-z0-9_]*)?\s*\{', re.M)
DEVICE_RE = re.compile(r'/\*\s*HMI Device Type:\s*([^*]+?)\s*\*/')


@dataclass
class HmiScreen:
    name: str
    path: str                      # "User-Defined Screens\Menus\Menu_Main" (as navigation targets spell it)
    folder: str                    # "User-Defined Screens\Menus"
    kind: str                      # user | predefined | banner
    nav_targets: list[str] = field(default_factory=list)
    popups: list[str] = field(default_factory=list)
    bindings: list[str] = field(default_factory=list)     # "controller.Tag.Member"
    aogs: list[str] = field(default_factory=list)
    security: dict = field(default_factory=dict)
    banner: bool = True
    source: str = ""


@dataclass
class HmiShortcut:
    name: str
    target: str
    caption: str = ""


@dataclass
class HmiExport:
    root: str
    project_name: str = ""
    device_type: str = ""
    home_screen: str = ""
    controllers: list[str] = field(default_factory=list)
    screens: list[HmiScreen] = field(default_factory=list)
    shortcuts: list[HmiShortcut] = field(default_factory=list)
    folders: list[str] = field(default_factory=list)
    aogs: list[str] = field(default_factory=list)
    documents: list[str] = field(default_factory=list)

    def screen(self, path_or_name: str) -> HmiScreen | None:
        key = path_or_name.replace("/", "\\")
        for s in self.screens:
            if s.path == key or s.name == key:
                return s
        return None


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8-sig", errors="replace")


def read_hmi_export(root: str | Path) -> HmiExport:
    root = Path(root)
    va = root / "ViewApplication.hmi"
    if not va.exists():
        raise FileNotFoundError(f"{root}: ViewApplication.hmi not found (View Designer > File > Export Project)")
    ex = HmiExport(root=str(root))
    text = _read(va)
    m = HEAD_RE.search(text)
    ex.project_name = m.group(2) if m else root.name
    dm = DEVICE_RE.search(text)
    ex.device_type = dm.group(1) if dm else ""
    hm = re.search(r'HomeScreen\s*:=\s*"([^"]*)"', text)
    ex.home_screen = hm.group(1) if hm else ""

    ex.aogs = sorted(p.stem for p in (root / "Assets" / "Add-On Graphics").glob("*.hmi"))
    ex.documents = sorted(p.name for p in (root / "Assets" / "Documents").glob("*") if p.is_file())
    ex.controllers = sorted(p.stem for p in (root / "Devices").glob("*.hmi"))
    aog_re = re.compile(r'AOG::([A-Za-z_][A-Za-z0-9_]*)\s+[A-Za-z_][A-Za-z0-9_]*\s*[({]')

    for p in sorted(root.rglob("*.hmi")):
        rel = p.relative_to(root).with_suffix("")
        parts = rel.parts
        if parts[0] in ("Assets", "Devices") or p.name == "ViewApplication.hmi":
            continue
        t = _read(p)
        if p.name == "__folder_properties.hmi":
            ex.folders.append("\\".join(parts[:-1]))
            continue
        head = HEAD_RE.search(t)
        if not head:
            continue
        kind_word, name = head.groups()
        if kind_word == "Banner":
            kind_word, name = "Screen", name or "Banner"
        path = "\\".join(parts)
        if kind_word == "Shortcut":
            tm = re.search(r'TargetScreenName\s*:=\s*"([^"]+)"', t)
            cm = re.search(r'Caption\s*:=\s*"([^"]*)"', t)
            ex.shortcuts.append(HmiShortcut(name=name, target=tm.group(1) if tm else "", caption=cm.group(1) if cm else name))
            continue
        if kind_word != "Screen":
            continue
        kind = "banner" if parts[0] == "Predefined Screens" and name == "Banner" else ("predefined" if parts[0] == "Predefined Screens" else "user")
        sec = {}
        sm = re.search(r'SecurityRoles\s*\{(.*?)\}', t, re.S)
        if sm:
            sec = {r: a for r, a in ROLE_RE.findall(sm.group(1))}
        s = HmiScreen(
            name=name, path=path, folder="\\".join(parts[:-1]), kind=kind,
            nav_targets=sorted(set(NAV_RE.findall(t))),
            popups=sorted({x for x in POPUP_RE.findall(t) if x}),
            bindings=sorted({f"{c}.{rest}" for c, rest in BIND_RE.findall(t) if c != "Local"}),
            aogs=sorted({m.group(1) for m in aog_re.finditer(t)}),
            security=sec,
            banner=not re.search(r'ShowDefaultBanner\s*:=\s*false', t),
            source=str(p.relative_to(root)),
        )
        ex.screens.append(s)
    ex.folders = sorted(set(ex.folders) | {s.folder for s in ex.screens if s.folder})
    return ex
