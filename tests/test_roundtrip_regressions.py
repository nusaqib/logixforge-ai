"""Regressions found on the SR RF HVPS project (docs/BACKLOG.md items 1-5): unnamed chassis modules,
multi-line routine descriptions, JSR calls from structured text, the online-write guard and SYSTEM.md ids."""
import copy
import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from logixforge.l5x.reader import export_project_dir, module_file_stem, read_l5x
from logixforge.l5x.writer import write_l5x
from logixforge.model import Module, Routine, Rung
from logixforge.project import load_project
from logixforge.validate import validate

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "examples" / "conveyor-demo"

UNNAMED_MODULE = (
    '<Module CatalogNumber="{cat}" Vendor="1" ProductType="7" ProductCode="391" Major="2" Minor="1" '
    'ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="false" SafetyEnabled="false">'
    '<EKey State="CompatibleModule" /><Ports><Port Id="1" Address="{slot}" Type="5069" Upstream="true" /></Ports></Module>'
)


def _demo_with_regression_content():
    proj = copy.deepcopy(load_project(DEMO))
    for slot, cat in ((1, "5069-IB16F/A"), (2, "5069-OB16/B")):
        proj.modules.append(Module(name="", catalog_number=cat, parent="Local", address=str(slot), port_type="5069",
                                   raw_xml=UNNAMED_MODULE.format(cat=cat, slot=slot)))
    prog = proj.programs[0]
    prog.routines.append(Routine(name="R_FromST", kind="RLL", description="- line one\n- line two\n   - indented three",
                                 rungs=[Rung(text="NOP();")]))
    prog.routines.append(Routine(name="R_StCaller", kind="ST", description="calls R_FromST from ST",
                                 st_lines=["// comment JSR(R_NotReal);", "JSR(R_FromST);"]))
    main = next(r for r in prog.routines if r.name == prog.main_routine)
    main.rungs.append(Rung(text="JSR(R_StCaller,0);"))
    return proj


def test_module_file_stem_for_unnamed_modules():
    m = Module(name="", catalog_number="5069-IB16F/A", parent="R01", address="3")
    assert module_file_stem(m) == "R01_S3_5069_IB16F"
    assert module_file_stem(Module(name="R01", catalog_number="5069-AENTR")) == "R01"


def test_unnamed_modules_survive_decompile_and_build(tmp_path):
    proj = _demo_with_regression_content()
    l5x = write_l5x(proj, str(tmp_path / "a.L5X"))
    back = read_l5x(l5x)
    assert sum(1 for m in back.modules if not m.name) == 2
    spec = export_project_dir(back, tmp_path / "spec")
    files = sorted(p.name for p in (spec / "modules").iterdir())
    assert "Local_S1_5069_IB16F.xml" in files and "Local_S2_5069_OB16.xml" in files and ".xml" not in files
    again = write_l5x(load_project(spec), str(tmp_path / "b.L5X"))
    mods = ET.parse(again).getroot().findall(".//Modules/Module")
    assert sorted(m.find("Ports/Port").get("Address") for m in mods if not m.get("Name")) == ["1", "2"]


def test_multiline_description_round_trips_and_builds(tmp_path):
    proj = _demo_with_regression_content()
    spec = export_project_dir(read_l5x(write_l5x(proj, str(tmp_path / "a.L5X"))), tmp_path / "spec")
    text = (spec / "programs" / proj.programs[0].name / "routines" / "R_FromST.rll").read_text(encoding="utf-8")
    assert text.startswith("//! - line one\n//! - line two\n//!    - indented three\nNOP();")
    loaded = load_project(spec)
    r = next(r for r in loaded.programs[0].routines if r.name == "R_FromST")
    assert r.description == "- line one\n- line two\n   - indented three"      # indentation survives the round trip
    rebuilt = ET.parse(write_l5x(loaded, str(tmp_path / "b.L5X"))).getroot()   # multi-line CDATA is well-formed XML
    assert rebuilt.find(".//Routine[@Name='R_FromST']/Description").text == r.description
    findings = validate(loaded)
    assert not [f for f in findings if f.code == "RUNG_SYNTAX"], [str(f) for f in findings if f.code == "RUNG_SYNTAX"]


def test_jsr_from_structured_text_counts_as_called():
    proj = _demo_with_regression_content()
    findings = validate(proj)
    uncalled = [f for f in findings if f.code == "ROUTINE_UNCALLED"]
    assert not [f for f in uncalled if "R_FromST" in f.where], [str(f) for f in uncalled]
    assert not [f for f in findings if f.code == "JSR_TARGET"]          # the commented-out JSR(R_NotReal) is ignored
    proj.programs[0].routines[-1].st_lines.append("JSR(R_Missing);")
    assert [f for f in validate(proj) if f.code == "JSR_TARGET" and "R_Missing" in f.message]


def test_system_md_ids_unique_for_unnamed_modules(tmp_path):
    from logixforge.docs.system import system_markdown
    proj = _demo_with_regression_content()
    md = system_markdown(proj, "", None, [], [])
    ids = [l.split("[")[0].strip() for l in md.splitlines() if l.strip().startswith("m_")]
    assert len(ids) == len(set(ids)) and "m_Local_S1" in ids and "m_Local_S2" in ids


def test_guard_ignores_file_write_in_inline_python():
    env = dict(os.environ)
    env.pop("LOGIXFORGE_ALLOW_ONLINE_WRITE", None)
    payload = {"tool_name": "Bash", "tool_input": {"command": "python - <<'EOF'\nopen('x.md', 'w').write(\"\\n\".join(out))\nEOF"}}
    r = subprocess.run([sys.executable, str(ROOT / "hooks" / "guard_online.py")], input=json.dumps(payload),
                       capture_output=True, text=True, env=env)
    assert r.returncode == 0
    payload["tool_input"]["command"] = "python -c \"from pycomm3 import LogixDriver; plc=LogixDriver('10.0.0.1'); plc.write(('Tag', 1))\""
    r = subprocess.run([sys.executable, str(ROOT / "hooks" / "guard_online.py")], input=json.dumps(payload),
                       capture_output=True, text=True, env=env)
    assert r.returncode == 2
