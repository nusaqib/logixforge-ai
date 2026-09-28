"""Studio 5000 View Designer import folder generator.

Output (import with File > Import Project > ViewApplication.hmi, View Designer v9+):

    <project_name>/
      ViewApplication.hmi
      Devices/<controller_ref>.hmi                 controller reference (when cip/acd paths are given)
      User-Defined Screens/[<Folder>/]<Screen>.hmi  (+ __folder_properties.hmi per folder)
      Assets/Add-On Graphics/AOG_<UDT>.hmi          one faceplate per UDT used
      Navigation Menu/<Screen>.hmi                  shortcut per screen (in_menu)

Syntax: Rockwell 9324-RM001 (Import/Export Reference Manual) corrected by real imports and by a
real View Designer v9 export (ALS-U masterHMI, 2715P-T15CD). Verified facts:
  * fill-colour animation = `ColorStateTable` with state property `fillcolor`; other animated
    properties use `StateTable` with proper-case property names (`Text`, `FillColor`, `ShowMark`)
  * button behaviours take `^Tag`; momentary = BehaviorSetTagTo1OnPress0OnRelease (+ minimumHoldTime)
  * NumericInput limits are `KeypadMinValue` / `KeypadMaxValue`; `BarGraph` (not BarGraph1); `Ellipse` exists
  * `ForceAnimations` is rejected; state tables need unique names; an empty HomeScreen is rejected
  * AOG instance: `<AOG> <name> ( <UserProp> := "::REF.Tag" ) { X..Access }`; screens carry
    `using ViewDesigner::AOG;` (accepted; Rockwell exports omit it)
"""
from __future__ import annotations

from pathlib import Path

from ..model import Project
from .spec import Faceplate, HmiSpec, Screen, Widget

BEHAVIORS = {
    "set1": "BehaviorSetTagTo1OnRelease", "set0": "BehaviorSetTagTo0OnRelease",
    "toggle": "BehaviorToggleTagOnRelease", "momentary": "BehaviorSetTagTo1OnPress0OnRelease",
}
AOG_USING = "using ViewDesigner::AOG;"
FONT = "Arial Unicode MS"
DEFAULT_COLORS = dict(bg="#ffffff", panel="#e7e8e9", border="#c8d0d8", text="#1f2933", label="#52606d",
                      button="#263a4e", button_text="#ffffff", nav="#3e5c76", accent="#00baff",
                      on="#51e79a", off="#7f8c8d", fault="#ff0000", input_bg="#fffbe6")

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
    if uses_aog:
        o.line(AOG_USING)
    o.line("")
    o.line(f"/* HMI Device Type: {spec.catalog} */")
    o.line("")


def _pos(o: _Out, x, y, w, h):
    o.line(f"X := {x:g};")
    o.line(f"Y := {y:g};")
    o.line(f"Width := {w:g};")
    o.line(f"Height := {h:g};")
    o.line("Angle := 0;")
    o.line("Enabled := true;")
    o.line("^Visible := true;")
    o.line("Opacity := 100;")
    o.line("Access := EnumElementAccessFamily.Inherit;")


def _border(o: _Out, color: str, width: float = 1, line: str = "SolidLine"):
    with o.block("Border"):
        o.line(f'Color := "{color or "#000000"}";')
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


def _color_state_table(o: _Out, binding: str, on_color: str, off_color: str):
    """Fill-colour animation (verified: ColorStateTable + lowercase 'fillcolor')."""
    with o.block(f"ColorStateTable {o.uid('ColorTable')}"):
        o.line(f'Expression := "" -> "{binding}";')
        with o.block(f'State State0 ( fillcolor := "{off_color}" )'):
            o.line('value := "0";')
        with o.block(f'State State1 ( fillcolor := "{on_color}" )'):
            o.line('value := "1";')
        with o.block(f'State DefaultState ( fillcolor := "{off_color}" )'):
            pass


def _state_table(o: _Out, binding: str, prop: str, off_val: str, on_val: str):
    """Generic animation (verified: StateTable + proper-case property names such as Text, FillColor, ShowMark)."""
    with o.block(f"StateTable {o.uid('StateTable')}"):
        o.line(f'Expression := "" -> "{binding}";')
        with o.block(f'State State0 ( {prop} := "{_esc(off_val)}" )'):
            o.line('value := "0";')
        with o.block(f'State State1 ( {prop} := "{_esc(on_val)}" )'):
            o.line('value := "1";')
        with o.block(f'State DefaultState ( {prop} := "{_esc(off_val)}" )'):
            pass


# ------------------------------------------------------------------ elements
class Emitter:
    def __init__(self, spec: HmiSpec):
        self.spec = spec
        self.c = dict(DEFAULT_COLORS, **spec.colors)
        self.font = spec.font_size

    def text_display(self, o, name, text, x, y, w, h, size=None, color=None, bold=False, align="HLEFT_VCENTER",
                     binding: str = "", fill="#00000000", state_binding="", off_text="", on_text=""):
        with o.block(f"TextDisplay {name}"):
            if binding:
                o.line(f'Text := "{_esc(text)}" -> "{binding}";')
            else:
                o.line(f'Text := "{_esc(text)}";')
            _font(o, size or self.font, color or self.c["text"], bold, align)
            o.line("Padding := 2;")
            o.line("CornerRadius := 0;")
            _border(o, "#000000", 1, "NoPen")
            o.line(f'FillColor := "{fill}";')
            if state_binding:
                _state_table(o, state_binding, "Text", off_text, on_text)
            _pos(o, x, y, w, h)

    def shape(self, o, name, x, y, w, h, fill, border=None, radius=4, kind="Rectangle", state_binding="",
              on_color="", off_color=""):
        with o.block(f"{kind} {name}"):
            if kind == "Rectangle":
                o.line(f"CornerRadius := {radius};")
            _border(o, border if border is not None else self.c["border"], 1, "SolidLine" if border != "" else "NoPen")
            o.line(f'FillColor := "{fill}";')
            if state_binding:
                _color_state_table(o, state_binding, on_color, off_color)
            _pos(o, x, y, w, h)

    def indicator(self, o, name, label, binding, x, y, w, h, on_color, off_color, on_text, off_text):
        """Label + lamp (Ellipse or Rectangle with ColorStateTable) + state text."""
        ellipse = self.spec.lamp_shape == "ellipse"
        lamp_w = min(120, w * 0.4)
        self.text_display(o, f"{name}_Lbl", label, x, y, w - lamp_w - GAP / 2, h, None, self.c["label"])
        if ellipse:
            d = min(h - 8, 28)
            self.shape(o, f"{name}_Lamp", x + w - lamp_w, y + (h - d) / 2, d, d, off_color, "#1e2e3e", 0, "Ellipse",
                       binding, on_color, off_color)
            self.text_display(o, f"{name}_Txt", off_text, x + w - lamp_w + d + 6, y, lamp_w - d - 6, h, None,
                              self.c["text"], True, "HLEFT_VCENTER", state_binding=binding, off_text=off_text, on_text=on_text)
        else:
            self.shape(o, f"{name}_Lamp", x + w - lamp_w, y + 4, lamp_w, h - 8, off_color, "", 6, "Rectangle",
                       binding, on_color, off_color)
            self.text_display(o, f"{name}_Txt", off_text, x + w - lamp_w, y + 4, lamp_w, h - 8, None, "#ffffff", True,
                              "HCENTER_VCENTER", state_binding=binding, off_text=off_text, on_text=on_text)

    def numeric(self, o, name, label, binding, x, y, w, h, decimals=0, units="", element="NumericDisplay",
                vmin=None, vmax=None):
        val_w = min(140, w * 0.45)
        self.text_display(o, f"{name}_Lbl", label + (f" [{units}]" if units else ""), x, y, w - val_w - GAP / 2, h,
                          None, self.c["label"])
        with o.block(f"{element} {name}_Val"):
            o.line("DigitsBeforeDecimal := 6;")
            o.line(f"DigitsAfterDecimal := {decimals};")
            o.line("LeadingZero := false;")
            o.line("TrailingZeros := false;")
            o.line("Rounding := EnumNumericRounding.Nearest;")
            o.line("LeadingZerosFill := false;")
            if element == "NumericInput":
                o.line("UsePredefinedDisabled := true;")
                o.line("MaskedValue := false;")
                o.line(f"KeypadMinValue := {vmin if vmin is not None else -999999:g};")
                o.line(f"KeypadMaxValue := {vmax if vmax is not None else 999999:g};")
                o.line("KeypadPosition := KeypadPositionEnum.MiddleCenter;")
            o.line(f'Value := 0 -> "{binding}";')
            _font(o, self.font + 1, self.c["text"], True, "HRIGHT_VCENTER")
            o.line("Padding := 4;")
            o.line("CornerRadius := 4;")
            _border(o, self.c["border"], 1, "SolidLine")
            o.line(f'FillColor := "{"#ffffff" if element == "NumericDisplay" else self.c["input_bg"]}";')
            _pos(o, x + w - val_w, y + 4, val_w, h - 8)

    def button(self, o, name, text, x, y, w, h, fill=None, nav_screen="", tag_binding="", action="set1"):
        with o.block(f"Button {name}"):
            o.line(f'FillColor := "{fill or self.c["button"]}";')
            _border(o, "#262324", 1)
            o.line("CornerRadius := 4;")
            o.line("TextAlignment := EnumAlignment.HCENTER_VCENTER;")
            o.line(f'FontName := "{FONT}";')
            o.line(f"FontSize := {self.font:g};")
            o.line(f'FontColor := "{self.c["button_text"]}";')
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
                    o.line(f'^Tag := "{tag_binding}";')
                    o.line("Key := EnumBezelKeys.VK_NONE;")
                    o.line("RequiresFocus := false;")
                    o.line("AlwaysTriggerReleaseEvent := true;")
                    if action == "momentary":
                        o.line("minimumHoldTime := 0;")
            _pos(o, x, y, w, h)

    def bargraph(self, o, name, label, binding, x, y, w, h, vmin=0, vmax=100):
        self.text_display(o, f"{name}_Lbl", label, x, y, w, 24, None, self.c["label"])
        with o.block(f"BarGraph {name}_Bar"):
            o.line(f'LevelColor := "{self.c["accent"]}";')
            o.line(f'FillColor := "{self.c["button"]}";')
            _border(o, "#918f8f", 1)
            o.line(f'Value := 0 -> "{binding}";')
            o.line(f"MinValue := {vmin:g};")
            o.line(f"MaxValue := {vmax:g};")
            _pos(o, x, y + 26, w, h - 26)


# ------------------------------------------------------------------ faceplate (Add-On Graphic)
def faceplate_size(fp: Faceplate, scale: float) -> tuple[float, float]:
    return FP_W * scale, (TITLE_H + len(fp.rows) * FP_ROW_H + 12) * scale


def aog_name(udt: str) -> str:
    return f"AOG_{udt}"


def aog_file(spec: HmiSpec, fp: Faceplate, proj: Project) -> str:
    o = _Out()
    em = Emitter(spec)
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
                o.line(f'DataType := "::{spec.controller_ref}.{fp.udt}";')
                o.line(f'Description := "{fp.udt} instance tag";')
                o.line('Category := "General";')
            with o.block("Title"):
                o.line(f'DataType := "::{spec.controller_ref}.STRING";')
                o.line('Description := "Faceplate title";')
                o.line('Category := "General";')
        em.shape(o, "Panel", 0, 0, w, h, em.c["panel"], em.c["border"], 6)
        em.text_display(o, "TitleTxt", fp.title or fp.udt, 8 * scale, 6 * scale, w - 16 * scale, (TITLE_H - 12) * scale,
                        em.font + 2, em.c["text"], True, "HLEFT_VCENTER", binding="Title")
        y = TITLE_H * scale
        rh = FP_ROW_H * scale
        inner_x, inner_w = 8 * scale, w - 16 * scale
        for i, r in enumerate(fp.rows):
            b = f"TagInstance.{r.member}"
            nm = f"R{i:02d}_{r.member}"
            if r.type == "indicator":
                em.indicator(o, nm, r.label or r.member, b, inner_x, y, inner_w, rh, r.on_color, r.off_color, r.on_text, r.off_text)
            elif r.type == "numeric":
                em.numeric(o, nm, r.label or r.member, b, inner_x, y, inner_w, rh, r.decimals or 0, r.units)
            elif r.type == "numeric_input":
                em.numeric(o, nm, r.label or r.member, b, inner_x, y, inner_w, rh, r.decimals or 0, r.units, "NumericInput", r.min, r.max)
            elif r.type == "button":
                em.button(o, nm, r.text or r.label or r.member, inner_x + inner_w * 0.5, y + 3 * scale, inner_w * 0.5,
                          rh - 6 * scale, tag_binding=b, action=r.action)
            y += rh
    return o.text()


# ------------------------------------------------------------------ screens
def screen_path(spec: HmiSpec, name: str) -> str:
    """'User-Defined Screens\\[Folder\\]Name' for navigation targets."""
    s = spec.screen(name)
    if s and s.folder:
        return f"User-Defined Screens\\{s.folder}\\{s.name}"
    return f"User-Defined Screens\\{name}"


def screen_file(spec: HmiSpec, s: Screen, proj: Project) -> str:
    o = _Out()
    em = Emitter(spec)
    _header(o, spec, uses_aog=any(w.type == "faceplate" for w in s.widgets))
    scale = spec.width / 1280
    ref = spec.controller_ref
    cols = max(1, s.columns)
    margin, gap = MARGIN * scale, GAP * scale
    cell_w = (spec.width - 2 * margin - (cols - 1) * gap) / cols
    cell_h = CELL_H * scale
    with o.block(f"Screen {s.name}"):
        o.line(f"ShowDefaultBanner := {'true' if spec.banner else 'false'};")
        o.line(f'FillColor := "{s.fill_color or em.c["bg"]}";')
        o.line("UpdateRate := EnumUpdateRate._500_ms;")
        em.text_display(o, "ScreenTitle", s.title or s.name, margin, 8 * scale, spec.width - 2 * margin, (TITLE_H - 8) * scale,
                        18, em.c["text"], True)
        col, row_y, row_h = 0, TITLE_H * scale + 8 * scale, cell_h
        for i, w in enumerate(s.widgets):
            span = max(1, min(cols, w.span))
            if w.type == "faceplate" and w.udt in spec.faceplates:
                fw, fh = faceplate_size(spec.faceplates[w.udt], scale)
                span = max(span, min(cols, int((fw + gap) // (cell_w + gap)) + 1))
                wh = fh
            elif w.type == "bargraph":
                wh = cell_h * 3
            else:
                wh = cell_h
            if col + span > cols:
                col, row_y, row_h = 0, row_y + row_h + gap, cell_h
            x = margin + col * (cell_w + gap)
            ww = span * cell_w + (span - 1) * gap
            nm = f"W{i:02d}_{_ident(w.tag or w.text or w.screen or w.type)}"
            bind = f"::{ref}.{w.tag}" if w.tag else ""
            if w.type == "text":
                em.text_display(o, nm, w.text, x, row_y, ww, wh)
            elif w.type == "indicator":
                em.shape(o, nm + "_Bg", x, row_y, ww, wh, em.c["panel"], em.c["border"], 6)
                em.indicator(o, nm, w.label or w.tag, bind, x + 8 * scale, row_y, ww - 16 * scale, wh, w.on_color, w.off_color,
                             w.on_text, w.off_text)
            elif w.type == "numeric":
                em.shape(o, nm + "_Bg", x, row_y, ww, wh, em.c["panel"], em.c["border"], 6)
                em.numeric(o, nm, w.label or w.tag, bind, x + 8 * scale, row_y, ww - 16 * scale, wh, w.decimals or 0, w.units)
            elif w.type == "numeric_input":
                em.shape(o, nm + "_Bg", x, row_y, ww, wh, em.c["panel"], em.c["border"], 6)
                em.numeric(o, nm, w.label or w.tag, bind, x + 8 * scale, row_y, ww - 16 * scale, wh, w.decimals or 0, w.units,
                           "NumericInput", w.min, w.max)
            elif w.type == "button":
                em.button(o, nm, w.text or w.label, x, row_y + 6 * scale, ww, wh - 12 * scale, tag_binding=bind, action=w.action)
            elif w.type == "nav_button":
                target = w.screen if "\\" in w.screen else screen_path(spec, w.screen)
                em.button(o, nm, w.text or w.screen, x, row_y + 6 * scale, ww, wh - 12 * scale, em.c["nav"], nav_screen=target)
            elif w.type == "bargraph":
                em.bargraph(o, nm, w.label or w.tag, bind, x, row_y, ww, wh, w.min or 0, w.max if w.max is not None else 100)
            elif w.type == "faceplate":
                fw, fh = faceplate_size(spec.faceplates[w.udt], scale)
                with o.block(f'{aog_name(w.udt)} {nm} ( TagInstance := "{bind}", Title := "{_esc(w.label or w.tag)}" )'):
                    _pos(o, x, row_y, fw, fh)
            row_h = max(row_h, wh)
            col += span
        o.line(f"Width := {spec.width};")
        o.line(f"Height := {(spec.screen_height if spec.banner else spec.height):g};")
        if s.security:
            with o.block("SecurityRoles"):
                for role, access in s.security.items():
                    o.line(f"{role} := RoleAccess.{access};")
    return o.text()


def _ident(s: str) -> str:
    s = "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in s)
    return s[:24].strip("_") or "W"


def shortcut_file(spec: HmiSpec, s: Screen) -> str:
    o = _Out()
    _header(o, spec)
    with o.block(f"Shortcut {s.name}"):
        o.line(f'TargetScreenName := "{screen_path(spec, s.name)}";')
        o.line("UseScreenSecurity := true;")
        o.line(f'Caption := "{_esc(s.title or s.name)}";')
    return o.text()


def folder_file(spec: HmiSpec, folder: str, security: dict | None) -> str:
    o = _Out()
    _header(o, spec)
    with o.block(f"ViewFolder {folder}"):
        if security:
            with o.block("SecurityRoles"):
                for role, access in security.items():
                    o.line(f"{role} := RoleAccess.{access};")
    return o.text()


def device_file(spec: HmiSpec) -> str:
    """Devices/<ref>.hmi - controller reference (verified syntax from a v9 export)."""
    o = _Out()
    _header(o, spec)
    with o.block(f"Controller {spec.controller_ref}"):
        o.line(f'CipPathFromHmiDevice := "{spec.cip_path}";')
        o.line(f'CipPathFromEmulator := "{spec.cip_path_emulator or spec.cip_path}";')
        o.line(f'ProjectFilePath := "{spec.acd_path}";')
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
    """Write one import package <name>/ (verified: imports in one pass into a fresh project)."""
    written = []
    root = Path(out_dir) / spec.project_name

    def w(rel: str, text: str):
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8", newline="\r\n")
        written.append(str(p))

    w("ViewApplication.hmi", view_application_file(spec))
    if spec.cip_path and spec.acd_path:
        w(f"Devices/{spec.controller_ref}.hmi", device_file(spec))
    for udt, fp in spec.faceplates.items():
        w(f"Assets/Add-On Graphics/{aog_name(udt)}.hmi", aog_file(spec, fp, proj))
    folders = {}
    for s in spec.screens:
        sub = f"{s.folder}/" if s.folder else ""
        w(f"User-Defined Screens/{sub}{s.name}.hmi", screen_file(spec, s, proj))
        if s.folder:
            folders[s.folder] = spec.folder_security.get(s.folder)
        if s.in_menu:
            w(f"Navigation Menu/{s.name}.hmi", shortcut_file(spec, s))
    for folder, sec in folders.items():
        w(f"User-Defined Screens/{folder}/__folder_properties.hmi", folder_file(spec, folder, sec))
    w("README_IMPORT.txt", _readme(spec))
    return written


def _readme(spec: HmiSpec) -> str:
    dev = (f"   The controller reference '{spec.controller_ref}' is included (Devices/); adjust the CIP path / ACD path there.\n"
           if spec.cip_path and spec.acd_path else
           f"   Add a controller reference named '{spec.controller_ref}' (Project Properties > References) pointing at the\n"
           f"   Logix Designer .ACD built from the same LogixForge project, or set hmi.json 'controller': {{cip_path, acd_path}}.\n")
    return f"""LogixForge View Designer import package: {spec.project_name}

Verified import procedure (View Designer v9+; an import with any error is discarded as a whole):
1. Create a project for a {spec.catalog} (or your terminal; imported screens are scaled to fit).
2. Controller reference: all bindings use '::{spec.controller_ref}.<Tag>'.
{dev}3. File > Import Project > this folder's ViewApplication.hmi (one pass; re-run for updates; same-named
   elements are overwritten and a backup .vpd is created).
4. Alarms: PanelView 5000 shows the controller's tag-based alarms (alarms.json in the PLC spec).
If the log rejects an element or property name, fix it in logixforge/hmi/viewdesigner.py and regenerate.
"""
