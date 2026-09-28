"""HMI navigation / hierarchy documentation (docs/generated/HMI_NAVIGATION.md).

One navigation model, two sources: the LogixForge `hmi/hmi.json` spec (screens, folders, nav buttons,
menu shortcuts) or a real View Designer export read by `logixforge.hmi.reader`.
"""
from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field

from ..hmi.reader import HmiExport
from ..hmi.spec import HmiSpec

USER = "User-Defined Screens"


@dataclass
class NavScreen:
    name: str
    path: str
    folder: str
    kind: str = "user"          # user | predefined | banner
    banner: bool = True
    security: dict = field(default_factory=dict)
    aogs: list[str] = field(default_factory=list)
    bindings: list[str] = field(default_factory=list)


@dataclass
class NavModel:
    title: str = ""
    device: str = ""
    home: str = ""
    controllers: list[str] = field(default_factory=list)
    screens: list[NavScreen] = field(default_factory=list)
    edges: list[tuple[str, str, str]] = field(default_factory=list)      # (src path, dst path, label)
    popups: list[tuple[str, str]] = field(default_factory=list)          # (src path, popup name)
    shortcuts: list[tuple[str, str]] = field(default_factory=list)       # (caption, target path)
    banner_targets: list[str] = field(default_factory=list)
    folders: list[str] = field(default_factory=list)
    aogs: list[str] = field(default_factory=list)
    source: str = ""

    def by_path(self) -> dict[str, NavScreen]:
        return {s.path: s for s in self.screens}


# ------------------------------------------------------------------ builders

def _norm(path: str) -> str:
    return path.replace("/", "\\")


def nav_from_export(ex: HmiExport) -> NavModel:
    m = NavModel(title=ex.project_name, device=ex.device_type, controllers=list(ex.controllers), folders=list(ex.folders),
                 aogs=list(ex.aogs), source="View Designer export")
    for s in ex.screens:
        m.screens.append(NavScreen(s.name, s.path, s.folder, s.kind, s.banner, dict(s.security), list(s.aogs), list(s.bindings)))
        if s.kind == "banner":
            m.banner_targets = list(s.nav_targets)
            continue
        for t in s.nav_targets:
            m.edges.append((s.path, _norm(t), ""))
        for pn in s.popups:
            m.popups.append((s.path, pn))
    home = ex.home_screen
    hs = ex.screen(home) if home else None
    m.home = hs.path if hs else (f"{USER}\\{home}" if home else "")
    m.shortcuts = [(sc.caption or sc.name, _norm(sc.target)) for sc in ex.shortcuts]
    return m


def nav_from_spec(spec: HmiSpec) -> NavModel:
    m = NavModel(title=spec.project_name, device=spec.catalog, controllers=[spec.controller_ref], aogs=[f"AOG_{u}" for u in spec.faceplates],
                 source="hmi/hmi.json")
    folders = set()
    for s in spec.screens:
        folder = f"{USER}\\{s.folder}" if s.folder else USER
        folders.add(folder)
        path = f"{folder}\\{s.name}"
        ns = NavScreen(s.name, path, folder, "user", spec.banner, dict(s.security))
        for w in s.widgets:
            if w.type == "nav_button" and w.screen:
                tgt = w.screen if "\\" in w.screen else next((f"{USER}\\{x.folder}\\{x.name}" if x.folder else f"{USER}\\{x.name}"
                                                             for x in spec.screens if x.name.lower() == w.screen.lower()), f"{USER}\\{w.screen}")
                m.edges.append((path, _norm(tgt), w.text or w.label))
            if w.tag:
                ns.bindings.append(f"{spec.controller_ref}.{w.tag}")
            if w.type == "faceplate":
                udt = w.udt or ""
                if udt:
                    ns.aogs.append(f"AOG_{udt}")
        ns.aogs = sorted(set(ns.aogs)); ns.bindings = sorted(set(ns.bindings))
        m.screens.append(ns)
        if s.in_menu:
            m.shortcuts.append((s.title or s.name, path))
    m.folders = sorted(folders)
    hs = next((x for x in m.screens if x.name.lower() == spec.home_screen.lower()), None)
    m.home = hs.path if hs else ""
    return m


# ------------------------------------------------------------------ analysis

def reachability(m: NavModel) -> tuple[set[str], set[str], list[tuple[str, str]]]:
    """(reachable paths, unreachable user screens, dangling (src, target) edges)."""
    paths = {s.path for s in m.screens}
    adj = defaultdict(set)
    for a, b, _ in m.edges:
        adj[a].add(b)
    entry = {m.home} | {t for _, t in m.shortcuts} | set(m.banner_targets)
    seen, stack = set(), [e for e in entry if e]
    while stack:
        n = stack.pop()
        if n in seen:
            continue
        seen.add(n)
        stack.extend(adj[n])
    unreachable = {s.path for s in m.screens if s.kind == "user" and s.path not in seen}
    dangling = [(a, b) for a, b, _ in m.edges if b not in paths and not b.startswith(("Predefined Screens\\", "Navigation Menu\\"))]
    return seen, unreachable, dangling


# ------------------------------------------------------------------ markdown

def _id(s: str) -> str:
    return "n_" + re.sub(r"[^A-Za-z0-9_]", "_", s)


def _leaf(path: str) -> str:
    return path.rsplit("\\", 1)[-1]


def _short(path: str) -> str:
    """Path without the 'User-Defined Screens\' prefix (keeps the folder so same-named screens stay distinct)."""
    return path[len(USER) + 1:] if path.startswith(USER + "\\") else path


def _q(label: str) -> str:
    """Mermaid label text inside double quotes."""
    return label.replace('"', "#quot;")


def _t(x) -> str:
    return str(x).replace("|", "\\|")


def hmi_navigation_markdown(m: NavModel, header: str = "") -> str:
    by = m.by_path()
    L = [header, f"# {m.title or 'HMI'} - screen hierarchy and navigation", "",
         f"Source: {m.source}. Terminal: {m.device or 'n/a'}. Home screen: `{m.home or 'not set'}`. "
         f"Controller reference(s): {', '.join(f'`{c}`' for c in m.controllers) or 'n/a'}. "
         f"{sum(1 for s in m.screens if s.kind == 'user')} user screens, {len(m.folders)} folders, {len(m.aogs)} Add-On Graphics.", ""]

    # hierarchy
    L += ["## Screen hierarchy (folders)", "", "```mermaid", "flowchart TD"]
    tree: dict[str, list[str]] = defaultdict(list)
    for s in m.screens:
        if s.kind != "banner":
            tree[s.folder].append(s.path)
    folders = sorted(set(m.folders) | set(tree))
    for f in folders:
        parent = f.rsplit("\\", 1)[0] if "\\" in f else ""
        L.append(f'  {_id(f)}[["{_leaf(f)}/"]]')
        if parent:
            L.append(f"  {_id(parent)} --> {_id(f)}")
    for f in folders:
        for p in sorted(tree.get(f, [])):
            s = by[p]
            mark = " *(home)*" if p == m.home else ""
            L.append(f'  {_id(f)} --> {_id(p)}("{_q(s.name)}{mark}")')
    L += ["```", ""]
    rows = []
    out_edges = defaultdict(list)
    for a, b, lbl in m.edges:
        out_edges[a].append(_leaf(b))
    for s in sorted(m.screens, key=lambda x: (x.kind != "user", x.path)):
        if s.kind == "banner":
            continue
        sec = ", ".join(f"{r}={a}" for r, a in s.security.items())
        rows.append(f"| {_t(s.name)} | {_t(s.folder)} | {'yes' if s.banner else 'no'} | {_t(sec)} | {_t(', '.join(s.aogs))} | {len(s.bindings)} | {_t(', '.join(sorted(set(out_edges[s.path]))))} |")
    L += ["| Screen | Folder | Banner | Security | Add-On Graphics | Bindings | Navigates to |", "|---|---|---|---|---|---|---|"] + rows + [""]

    # menu
    L += ["## Navigation menu (shortcuts)", ""]
    if m.shortcuts:
        L += ["| Caption | Target |", "|---|---|"] + [f"| {_t(c)} | `{_t(t)}` |" for c, t in m.shortcuts] + [""]
    else:
        L += ["(no shortcuts; screens are reached by navigation buttons only)", ""]
    if m.banner_targets:
        L += ["## Banner (available from every screen)", "", "| Target |", "|---|"] + [f"| `{_t(t)}` |" for t in m.banner_targets] + [""]

    # graph
    L += ["## Navigation graph", "", "Solid arrows = navigation buttons on the screen; dashed = popups. Predefined screens are shown as boxes; the banner targets are omitted to keep the graph readable.", "",
          "```mermaid", "flowchart LR"]
    nodes = set()
    for s in m.screens:
        if s.kind == "user":
            mark = " (home)" if s.path == m.home else ""
            L.append(f'  {_id(s.path)}("{_q(s.name)}{mark}")')
            nodes.add(s.path)
    for a, b, lbl in m.edges:
        if a not in nodes:
            continue
        if b not in nodes:
            L.append(f'  {_id(b)}["{_leaf(b)}"]')
            nodes.add(b)
        L.append(f"  {_id(a)} -->{('|' + _q(lbl).replace('|', '/') + '|') if lbl else ''} {_id(b)}")
    for a, pn in m.popups:
        if a in nodes:
            L.append(f'  {_id(a)} -.-> {_id("popup_" + pn)}[/"{pn}"/]')
    if m.home:
        L.append(f"  style {_id(m.home)} stroke-width:3px")
    L += ["```", ""]

    # reachability
    seen, unreachable, dangling = reachability(m)
    dead_ends = [s for s in m.screens if s.kind == "user" and not out_edges[s.path] and not m.banner_targets and s.path not in {t for _, t in m.shortcuts}]
    L += ["## Checks", ""]
    L.append(f"- Reachable from home/menu/banner: {sum(1 for s in m.screens if s.kind == 'user' and s.path in seen)} of {sum(1 for s in m.screens if s.kind == 'user')} user screens.")
    L.append("- Unreachable screens (no shortcut, no banner entry, no button leads here): " + (", ".join(f"`{_short(u)}`" for u in sorted(unreachable)) if unreachable else "none") + ".")
    L.append("- Navigation targets that do not exist: " + (", ".join(f"`{_short(a)}` -> `{b}`" for a, b in dangling) if dangling else "none") + ".")
    if dead_ends:
        L.append("- Screens with no way out except the terminal's navigation menu: " + ", ".join(f"`{s.name}`" for s in dead_ends) + ".")
    L.append("")

    # AOGs
    if m.aogs:
        use = defaultdict(list)
        for s in m.screens:
            for a in s.aogs:
                use[a].append(s.name)
        L += ["## Add-On Graphics usage", "", "| Add-On Graphic | Used on |", "|---|---|"]
        L += [f"| {a} | {_t(', '.join(sorted(use.get(a, []))) or '(unused)')} |" for a in m.aogs] + [""]

    # bindings
    L += ["## Tag bindings per screen", "", "Top-level controller tags each screen reads or writes (members collapsed). Full list per tag in HMI_TAGS.md.", "",
          "| Screen | Bindings | Tags |", "|---|---|---|"]
    for s in sorted(m.screens, key=lambda x: x.path):
        if s.kind == "banner" or not s.bindings:
            continue
        tops = sorted({re.split(r"[.:\[]", b.split(".", 1)[1] if "." in b else b)[0] for b in s.bindings})
        L.append(f"| {_t(s.name)} | {len(s.bindings)} | {_t(', '.join(tops))} |")
    L.append("")
    return "\n".join(L)
