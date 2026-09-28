"""Studio 5000 View Designer import folder generator.

Output (import with File > Import Project > ViewApplication.hmi, View Designer v9+):

    <project_name>/
      ViewApplication.hmi
      User-Defined Screens/<Screen>.hmi
      Assets/Add-On Graphics/AOG_<UDT>.hmi        one faceplate per UDT used
      Navigation Menu/<Screen>.hmi                 shortcut per screen (in_menu)

Syntax follows Rockwell 9324-RM001 (Import/Export Reference Manual). Element and property names
verified against the manual's examples are used everywhere possible; the few names that are not
in the manual are collected in UNVERIFIED so a failed import can be fixed in one place.
"""
from __future__ import annotations

from pathlib import Path

from ..model import Project
from .spec import Faceplate, HmiSpec, Screen, Widget

# --- names the manual does not show verbatim; adjust here if View Designer rejects them -----------
# Import round 1 (View Designer, 2026-09-28) proved: NumericInput and BehaviorSetTagTo1OnRelease exist as
# element types; 'TagName' is not the behavior's property; MinValue/MaxValue are not NumericInput members;
# 'ForceAnimations' is not accepted on elements or screens; a StateTable named 'StateTable' fails to parse.
# Import round 2 proved: '^Tag', StateTable state props 'fillcolor'/'text' and the UDT-typed AOG user
# property all import clean. Round 3: a screen can only instantiate an AOG that already exists in the project
# (any unresolved reference discards the whole import), so AOGs ship as a separate first-pass package.
UNVERIFIED = {
    "numeric_input_element": "NumericInput",          # element type confirmed; its min/max property names unknown
    "behavior_tag_property": "^Tag",                 # 'tag' is a caret-keyword; 'TagName' rejected
    "state_fillcolor_property": "fillcolor",         # StateTable state property for FillColor
    "state_text_property": "text",                   # StateTable state property for Text
    "aog_udt_datatype_prefix": "::{ref}.{udt}",      # AOG user property DataType for a UDT
}
EMIT_FORCE_ANIMATIONS = False                        # rejected by View Designer on import
AOG_USING = "using ViewDesigner::AOG;"               # screens instantiating user AOGs: round 2 failed without it
BEHAVIORS = {"set1": "BehaviorSetTagTo1OnRelease", "set0": "BehaviorSetTagTo0OnRelease", "toggle": "BehaviorToggleTagOnRelease"}

FONT = "Arial Unicode MS"
COLORS = dict(bg="#f4f6f8", panel="#ffffff", border="#c8d0d8", text="#1f2933", label="#52606d",
              button="#263a4e", button_text="#ffffff", nav="#3e5c76", accent="#29abe2")

# layout constants (pixels at 1280 wide; scaled by spec.width/1280)
CELL_W, CELL_H, GAP, MARGIN, TITLE_H = 380, 60, 16, 24, 48
FP_ROW_H, FP_W, FP_LABEL_W = 34, 380, 170


class _Out:
    def __init__(self):
        self.lines: list[str] = []
        self.depth = 0
        self.n = 0

    def uid(self, prefix: str) -> str:
        self.n += 1
        return f"{prefix}_{self.n:03d}"

    def line(self, s: str):
        self.lines.append("\t" * self.depth + s)

    def block(self, header: str):
        o = self

        class _B:
            def __enter__(s):
                o.line(header + " {")
                o.depth += 1

            def __exit__(s, *a):
                o.depth -= 1
                o.line("}")
        return _B()

    def text(self) -> str:
        return "\n".join(self.lines) + "\n"


def _esc(s: str) -> str:
    return s.replace('"', '$"')


def _header(o: _Out, spec: HmiSpec, aog: bool = False, uses_aog: bool = False):
    o.line(f"namespace ViewDesigner{'::AOG' if aog else ''};")
    o.line("using HMICatalog;")
    if uses_aog and AOG_USING:
        o.line(AOG_USING)
    o.line("")
    o.line(f"/* HMI Device Type: {spec.catalog} */")
    o.line("")


def _pos(o: _Out, x, y, w, h, force_anim: bool = True):
    o.line(f"X := {x:g};")
    o.line(f"Y := {y:g};")
    o.line(f"Width := {w:g};")
    o.line(f"Height := {h:g};")
    o.line("Angle := 0;")
    o.line("Enabled := true;")
    o.line("^Visible := true;")
    o.line("Opacity := 100;")
    o.line("Access := EnumElementAccessFamily.Inherit;")
    if force_anim and EMIT_FORCE_ANIMATIONS:
        o.line("ForceAnimations := false;")


def _border(o: _Out, color: str, width: float = 1, line: str = "SolidLine"):
    with o.block("Border"):
        o.line(f'Color := "{color}";')
        with o.block("BorderStyle"):
            o.line(f"Line := PenStyle.{line};")
            o.line("Cap := CapStyle.SquareCap;")
            o.line("Join := JoinStyle.MiterJoin;")
        o.line(f"Width := {width:g};")


def _font(o: _Out, size: float, color: str, bold: bool = False, align: str = "HLEFT_VCENTER"):
    o.line(f'FontName := "{FONT}";')
    o.line(f"FontSize := {size:g};")
    o.line(f"Bold := {'true' if bold else 'false'};")
    o.line("Underline := false;")
    o.line(f'FontColor := "{color}";')
    o.line(f"TextAlignment := EnumAlignment.{align};")


# ------------------------------------------------------------------ elements
def text_display(o, name, text, x, y, w, h, size=12, color=COLORS["text"], bold=False, align="HLEFT_VCENTER",
                 binding: str = "", fill="#00000000", force_anim=True):
    with o.block(f"TextDisplay {name}"):
        if binding:
            o.line(f'Text := "{_esc(text)}" -> "{binding}";')
        else:
            o.line(f'Text := "{_esc(text)}";')
        _font(o, size, color, bold, align)
        o.line("Padding := 2;")
        o.line("CornerRadius := 0;")
        _border(o, "#000000", 1, "NoPen")
        o.line(f'FillColor := "{fill}";')
        _pos(o, x, y, w, h, force_anim)


def rectangle(o, name, x, y, w, h, fill, border=COLORS["border"], radius=4, force_anim=True, state_binding="",
              on_color="", off_color=""):
    with o.block(f"Rectangle {name}"):
        o.line(f"CornerRadius := {radius};")
        _border(o, border or "#000000", 1, "SolidLine" if border else "NoPen")
        o.line(f'FillColor := "{fill}";')
        if state_binding:
            fc = UNVERIFIED["state_fillcolor_property"]
            with o.block(f"StateTable {o.uid('StateTable')}"):
                o.line(f'Expression := "" -> "{state_binding}";')
                with o.block(f'State State0 ( {fc} := "{off_color}" )'):
                    o.line('value := "0";')
                with o.block(f'State State1 ( {fc} := "{on_color}" )'):
                    o.line('value := "1";')
                with o.block(f'State DefaultState ( {fc} := "{off_color}" )'):
                    pass
        _pos(o, x, y, w, h, force_anim)


def indicator(o, name, label, binding, x, y, w, h, on_color, off_color, on_text, off_text, force_anim=True):
    """Label + colored lamp with state text (Rectangle + TextDisplay driven by one BOOL)."""
    lamp_w = min(120, w * 0.4)
    text_display(o, f"{name}_Lbl", label, x, y, w - lamp_w - GAP / 2, h, 12, COLORS["label"], False, "HLEFT_VCENTER",
                 force_anim=force_anim)
    rectangle(o, f"{name}_Lamp", x + w - lamp_w, y + 4, lamp_w, h - 8, off_color, "", 6, force_anim, binding, on_color, off_color)
    tp = UNVERIFIED["state_text_property"]
    with o.block(f"TextDisplay {name}_Txt"):
        o.line(f'Text := "{_esc(off_text)}";')
        _font(o, 11, "#ffffff", True, "HCENTER_VCENTER")
        o.line("Padding := 0;")
        o.line("CornerRadius := 0;")
        _border(o, "#000000", 1, "NoPen")
        o.line('FillColor := "#00000000";')
        with o.block(f"StateTable {o.uid('StateTable')}"):
            o.line(f'Expression := "" -> "{binding}";')
            with o.block(f'State State0 ( {tp} := "{_esc(off_text)}" )'):
                o.line('value := "0";')
            with o.block(f'State State1 ( {tp} := "{_esc(on_text)}" )'):
                o.line('value := "1";')
            with o.block(f'State DefaultState ( {tp} := "{_esc(off_text)}" )'):
                pass
        _pos(o, x + w - lamp_w, y + 4, lamp_w, h - 8, force_anim)


def numeric_display(o, name, label, binding, x, y, w, h, decimals=0, units="", force_anim=True, element="NumericDisplay",
                    vmin=None, vmax=None):
    val_w = min(140, w * 0.45)
    text_display(o, f"{name}_Lbl", label + (f" [{units}]" if units else ""), x, y, w - val_w - GAP / 2, h, 12,
                 COLORS["label"], False, "HLEFT_VCENTER", force_anim=force_anim)
    with o.block(f"{element} {name}_Val"):
        o.line("DigitsBeforeDecimal := 6;")
        o.line(f"DigitsAfterDecimal := {decimals};")
        o.line("LeadingZero := false;")
        o.line("TrailingZeros := false;")
        o.line("Rounding := EnumNumericRounding.Nearest;")
        o.line("LeadingZerosFill := false;")
        # NumericInput limits: View Designer rejected MinValue/MaxValue; enforce ranges in the PLC (Cfg_ clamp) for now
        o.line(f'Value := 0 -> "{binding}";')
        _font(o, 14, COLORS["text"], True, "HRIGHT_VCENTER")
        o.line("Padding := 4;")
        o.line("CornerRadius := 4;")
        _border(o, COLORS["border"], 1, "SolidLine")
        o.line(f'FillColor := "{"#ffffff" if element == "NumericDisplay" else "#fffbe6"}";')
        _pos(o, x + w - val_w, y + 4, val_w, h - 8, force_anim)


def button(o, name, text, x, y, w, h, fill=COLORS["button"], force_anim=True, nav_screen="", tag_binding="", action="set1"):
    with o.block(f"Button {name}"):
        o.line(f'FillColor := "{fill}";')
        _border(o, "#262324", 1)
        o.line("CornerRadius := 4;")
        o.line("TextAlignment := EnumAlignment.HCENTER_VCENTER;")
        o.line(f'FontName := "{FONT}";')
        o.line("FontSize := 12;")
        o.line(f'FontColor := "{COLORS["button_text"]}";')
        o.line("Bold := true;")
        o.line(f'Text := "{_esc(text)}";')
        o.line("UsePredefinedDisabled := true;")
        if nav_screen:
            with o.block(f"BehaviorNavigateToScreen {o.uid('BehaviorNavigateToScreen')}"):
                o.line(f'screenName := "{nav_screen}";')
                o.line("Key := EnumBezelKeys.VK_NONE;")
                o.line("RequiresFocus := false;")
                o.line("AlwaysTriggerReleaseEvent := false;")
        elif tag_binding:
            beh = BEHAVIORS.get(action, BEHAVIORS["set1"])
            with o.block(f"{beh} {o.uid(beh)}"):
                o.line(f'{UNVERIFIED["behavior_tag_property"]} := "{tag_binding}";')
                o.line("Key := EnumBezelKeys.VK_NONE;")
                o.line("RequiresFocus := false;")
                o.line("AlwaysTriggerReleaseEvent := false;")
        _pos(o, x, y, w, h, force_anim)


def bargraph(o, name, label, binding, x, y, w, h, vmin=0, vmax=100, force_anim=True):
    text_display(o, f"{name}_Lbl", label, x, y, w, 24, 12, COLORS["label"], False, "HLEFT_VCENTER", force_anim=force_anim)
    with o.block(f"BarGraph1 {name}_Bar"):
        o.line('FillColor := "#4d4d4d";')
        o.line("FillOpacity := 100;")
        o.line("TickMarkOpacity := 100;")
        o.line("TextOpacity := 100;")
        o.line(f'LevelColor := "{COLORS["accent"]}";')
        o.line(f'Value := 0 -> "{binding}";')
        o.line(f"MinValue := {vmin:g};")
        o.line(f"MaxValue := {vmax:g};")
        o.line('HousingColor := "#333333";')
        o.line('TickMarkColor := "#f2f2f2";')
        o.line(f'FontName := "{FONT}";')
        o.line("FontSize := 10;")
        o.line('FontColor := "#ffffff";')
        _pos(o, x, y + 26, w, h - 26, force_anim)


# ------------------------------------------------------------------ faceplate (Add-On Graphic)
def faceplate_size(fp: Faceplate, scale: float) -> tuple[float, float]:
    rows = len(fp.rows)
    return FP_W * scale, (TITLE_H + rows * FP_ROW_H + 12) * scale


def aog_name(udt: str) -> str:
    return f"AOG_{udt}"


def aog_file(spec: HmiSpec, fp: Faceplate, proj: Project) -> str:
    o = _Out()
    _header(o, spec, aog=True)
    scale = spec.width / 1280
    w, h = faceplate_size(fp, scale)
    with o.block(f"AddOnGraphic {aog_name(fp.udt)}"):
        o.line(f'Description := "{_esc(fp.title or fp.udt)} faceplate (generated by LogixForge)";')
        o.line('Vendor := "LogixForge";')
        o.line("Major := 1;")
        o.line("Minor := 0;")
        o.line('Extended := "";')
        o.line('Note := "";')
        o.line(f"Width := {w:g};")
        o.line(f"Height := {h:g};")
        o.line(f"TerminalWidth := {spec.width};")
        o.line(f"TerminalHeight := {spec.height};")
        with o.block("UserProperties"):
            with o.block("TagInstance"):
                o.line(f'DataType := "{UNVERIFIED["aog_udt_datatype_prefix"].format(ref=spec.controller_ref, udt=fp.udt)}";')
                o.line(f'Description := "{fp.udt} instance tag";')
                o.line('Category := "General";')
            with o.block("Title"):
                o.line('DataType := "::LGX.STRING";'.replace("LGX", spec.controller_ref))
                o.line('Description := "Faceplate title";')
                o.line('Category := "General";')
        # panel background + title
        rectangle(o, "Panel", 0, 0, w, h, COLORS["panel"], COLORS["border"], 6, force_anim=False)
        text_display(o, "TitleTxt", fp.title or fp.udt, 8 * scale, 6 * scale, w - 16 * scale, (TITLE_H - 12) * scale, 14,
                     COLORS["text"], True, "HLEFT_VCENTER", binding="Title", force_anim=False)
        y = TITLE_H * scale
        rh = FP_ROW_H * scale
        inner_x, inner_w = 8 * scale, w - 16 * scale
        for i, r in enumerate(fp.rows):
            b = f"TagInstance.{r.member}"
            nm = f"R{i:02d}_{r.member}"
            if r.type == "indicator":
                indicator(o, nm, r.label or r.member, b, inner_x, y, inner_w, rh, r.on_color, r.off_color, r.on_text, r.off_text, False)
            elif r.type == "numeric":
                numeric_display(o, nm, r.label or r.member, b, inner_x, y, inner_w, rh, r.decimals or 0, r.units, False)
            elif r.type == "numeric_input":
                numeric_display(o, nm, r.label or r.member, b, inner_x, y, inner_w, rh, r.decimals or 0, r.units, False,
                                UNVERIFIED["numeric_input_element"], r.min, r.max)
            elif r.type == "button":
                button(o, nm, r.text or r.label or r.member, inner_x + inner_w * 0.5, y + 3 * scale, inner_w * 0.5, rh - 6 * scale,
                       COLORS["button"], False, tag_binding=b, action=r.action)
            y += rh
    return o.text()


# ------------------------------------------------------------------ screens
def screen_file(spec: HmiSpec, s: Screen, proj: Project) -> str:
    o = _Out()
    _header(o, spec, uses_aog=any(w.type == "faceplate" for w in s.widgets))
    scale = spec.width / 1280
    ref = spec.controller_ref
    cols = max(1, s.columns)
    margin, gap = MARGIN * scale, GAP * scale
    cell_w = (spec.width - 2 * margin - (cols - 1) * gap) / cols
    cell_h = CELL_H * scale
    with o.block(f"Screen {s.name}"):
        o.line("ShowDefaultBanner := true;")
        o.line(f'FillColor := "{s.fill_color}";')
        o.line("UpdateRate := EnumUpdateRate._500_ms;")
        text_display(o, "ScreenTitle", s.title or s.name, margin, 8 * scale, spec.width - 2 * margin, (TITLE_H - 8) * scale,
                     18, COLORS["text"], True)
        # grid placement: widgets flow left-to-right; faceplates occupy their own height
        col, row_y, row_h = 0, TITLE_H * scale + 8 * scale, cell_h
        for i, w in enumerate(s.widgets):
            span = max(1, min(cols, w.span))
            if w.type == "faceplate" and w.udt in spec.faceplates:
                fw, fh = faceplate_size(spec.faceplates[w.udt], scale)
                span = max(span, min(cols, int((fw + gap) // (cell_w + gap)) + 1))
                wh = fh
            else:
                wh = cell_h
            if col + span > cols:
                col, row_y, row_h = 0, row_y + row_h + gap, cell_h
            x = margin + col * (cell_w + gap)
            ww = span * cell_w + (span - 1) * gap
            nm = f"W{i:02d}_{_ident(w.tag or w.text or w.screen or w.type)}"
            bind = f"::{ref}.{w.tag}" if w.tag else ""
            if w.type == "text":
                text_display(o, nm, w.text, x, row_y, ww, wh, 12, COLORS["text"], False)
            elif w.type == "indicator":
                rectangle(o, nm + "_Bg", x, row_y, ww, wh, COLORS["panel"], COLORS["border"], 6)
                indicator(o, nm, w.label or w.tag, bind, x + 8 * scale, row_y, ww - 16 * scale, wh, w.on_color, w.off_color,
                          w.on_text, w.off_text)
            elif w.type == "numeric":
                rectangle(o, nm + "_Bg", x, row_y, ww, wh, COLORS["panel"], COLORS["border"], 6)
                numeric_display(o, nm, w.label or w.tag, bind, x + 8 * scale, row_y, ww - 16 * scale, wh, w.decimals or 0, w.units)
            elif w.type == "numeric_input":
                rectangle(o, nm + "_Bg", x, row_y, ww, wh, COLORS["panel"], COLORS["border"], 6)
                numeric_display(o, nm, w.label or w.tag, bind, x + 8 * scale, row_y, ww - 16 * scale, wh, w.decimals or 0, w.units,
                                True, UNVERIFIED["numeric_input_element"], w.min, w.max)
            elif w.type == "button":
                button(o, nm, w.text or w.label, x, row_y + 6 * scale, ww, wh - 12 * scale, COLORS["button"], True,
                       tag_binding=bind, action=w.action)
            elif w.type == "nav_button":
                target = w.screen if "\\" in w.screen else f"User-Defined Screens\\{w.screen}"
                button(o, nm, w.text or w.screen, x, row_y + 6 * scale, ww, wh - 12 * scale, COLORS["nav"], True, nav_screen=target)
            elif w.type == "bargraph":
                wh = cell_h * 3
                bargraph(o, nm, w.label or w.tag, bind, x, row_y, ww, wh, w.min or 0, w.max if w.max is not None else 100)
            elif w.type == "faceplate":
                fp = spec.faceplates[w.udt]
                fw, fh = faceplate_size(fp, scale)
                with o.block(f'{aog_name(w.udt)} {nm} ( TagInstance := "{bind}", Title := "{_esc(w.label or w.tag)}" )'):
                    _pos(o, x, row_y, fw, fh)
            row_h = max(row_h, wh)
            col += span
        o.line(f"Width := {spec.width};")
        o.line(f"Height := {spec.screen_height:g};")
        if EMIT_FORCE_ANIMATIONS:
            o.line("ForceAnimations := false;")
    return o.text()


def _ident(s: str) -> str:
    s = "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in s)
    return s[:24].strip("_") or "W"


def shortcut_file(spec: HmiSpec, s: Screen) -> str:
    o = _Out()
    _header(o, spec)
    with o.block(f"Shortcut {s.name}"):
        o.line(f'TargetScreenName := "User-Defined Screens\\{s.name}";')
        o.line("UseScreenSecurity := true;")
        o.line(f'Caption := "{_esc(s.title or s.name)}";')
    return o.text()


def view_application_file(spec: HmiSpec, home_screen: bool = True) -> str:
    o = _Out()
    o.line("namespace ViewDesigner;")
    o.line("using HMICatalog;")
    o.line("")
    o.line(f"/* HMI Device Type: {spec.catalog} */")
    o.line("/* Generated by LogixForge - import with File > Import Project */")
    o.line("")
    with o.block(f"ViewProject {spec.project_name}"):
        # an empty HomeScreen is rejected ("Home Screen does not exist"); omit it to keep the project's current one
        if home_screen and spec.home_screen:
            o.line(f'HomeScreen := "{spec.home_screen}";')
    return o.text()


def build_viewdesigner(proj: Project, spec: HmiSpec, out_dir: str | Path) -> list[str]:
    """Write two import packages:
       <name>_1_AddOnGraphics/   import FIRST on a fresh project (screens can only reference AOGs that already exist;
                                 an import with any unresolved reference is discarded as a whole)
       <name>/                   everything (screens, shortcuts, AOGs); use for re-imports/updates
    """
    written = []

    def w(root: Path, rel: str, text: str):
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8", newline="\r\n")
        written.append(str(p))

    aogs = {udt: aog_file(spec, fp, proj) for udt, fp in spec.faceplates.items()}
    if aogs:
        stage1 = Path(out_dir) / f"{spec.project_name}_1_AddOnGraphics"
        w(stage1, "ViewApplication.hmi", view_application_file(spec, home_screen=False))
        for udt, text in aogs.items():
            w(stage1, f"Assets/Add-On Graphics/{aog_name(udt)}.hmi", text)
    root = Path(out_dir) / spec.project_name
    w(root, "ViewApplication.hmi", view_application_file(spec))
    for udt, text in aogs.items():
        w(root, f"Assets/Add-On Graphics/{aog_name(udt)}.hmi", text)
    for s in spec.screens:
        w(root, f"User-Defined Screens/{s.name}.hmi", screen_file(spec, s, proj))
        if s.in_menu:
            w(root, f"Navigation Menu/{s.name}.hmi", shortcut_file(spec, s))
    w(root, "README_IMPORT.txt", _readme(spec))
    return written


def _readme(spec: HmiSpec) -> str:
    return f"""LogixForge View Designer import package: {spec.project_name}

Verified import procedure (View Designer; an import with any error is discarded as a whole):
1. In Studio 5000 View Designer (v9 or later) create a project for a {spec.catalog}
   (or the terminal you use; imported screens are scaled to fit).
2. Add a controller reference named '{spec.controller_ref}' that points at the Logix Designer .ACD
   built from the same LogixForge project (Project Properties > References). All bindings use
   '::{spec.controller_ref}.<Tag>'.
3. FIRST TIME ONLY: File > Import Project > ../{spec.project_name}_1_AddOnGraphics/ViewApplication.hmi
   (screens can only reference Add-On Graphics that already exist in the project).
4. File > Import Project > this folder's ViewApplication.hmi (screens, shortcuts, AOGs; re-run for updates).
5. Alarms: PanelView 5000 shows the controller's tag-based alarms (alarms.json in the PLC spec);
   the Alarm Summary / Alarm Manager predefined screens need no configuration.
If the log rejects an element or property name, see logixforge/hmi/viewdesigner.py (UNVERIFIED /
EMIT_* constants), change it, and regenerate with `lf hmi build`.
"""
