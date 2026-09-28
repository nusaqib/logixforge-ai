import xml.etree.ElementTree as ET
from pathlib import Path

from logixforge.hmi.docs import write_hmi_docs
from logixforge.hmi.spec import load_hmi_spec
from logixforge.hmi.viewdesigner import build_viewdesigner
from logixforge.l5x.reader import export_project_dir, read_l5x
from logixforge.l5x.writer import write_l5x
from logixforge.project import load_project
from logixforge.validate import has_errors, validate

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "examples" / "conveyor-demo"


def test_alarms_in_l5x_and_round_trip(tmp_path):
    proj = load_project(DEMO)
    assert [a.name for a in proj.alarms] == ["Conveyor01_Fault", "ESTOP_Active", "SimMode_Active"]
    assert not has_errors(validate(proj))
    out = write_l5x(proj, str(tmp_path / "d.L5X"))
    ctl = ET.parse(out).getroot().find("Controller")
    tag = ctl.find("Tags/Tag[@Name='Alarms']")
    conds = tag.findall("AlarmConditions/AlarmCondition")
    assert len(conds) == 3
    c = conds[0]
    assert c.get("Input") == ".Conveyor01_Fault" and c.get("ConditionType") == "TRIP" and c.get("Severity") == "750"
    assert c.get("EvaluationGroup") == "500 millisecond" and c.get("AckRequired") == "true"
    assert c.find("AlarmConfig/Messages/Message[@Type='CAM']/Text").get("Lang") == "en-US"
    assert "run feedback missing" in Path(out).read_text(encoding="utf-8")
    # AlarmConditions must precede Data inside the tag
    kids = [k.tag for k in tag]
    assert kids.index("Description") < kids.index("AlarmConditions")
    hmi = ctl.find("Tags/Tag[@Name='HMI_Conveyor01']")
    assert [k.tag for k in hmi] == ["Description", "Data"]        # no AlarmConditions on tags without alarms
    back = read_l5x(out)
    assert {a.name for a in back.alarms} == {a.name for a in proj.alarms}
    assert back.alarms[1].message.startswith("Emergency stop")
    spec = export_project_dir(back, tmp_path / "spec")
    again = load_project(spec)
    assert [a.input_path for a in again.alarms] == [a.input_path for a in proj.alarms]


def test_alarm_validation(tmp_path):
    import json
    import shutil
    shutil.copytree(DEMO, tmp_path / "p")
    (tmp_path / "p" / "alarms.json").write_text(json.dumps([
        {"name": "Bad1", "input": "Nope.X", "message": "m"},
        {"name": "Bad2", "input": "Alarms.NotAMember", "message": "m"},
        {"name": "Bad3", "input": "Alarms.ESTOP", "condition": "HI", "message": "m"},
        {"name": "Bad4", "input": "HMI_Conveyor01.Sts_RunHours", "condition": "TRIP", "severity": 5000},
    ]), encoding="utf-8")
    codes = {f.code for f in validate(load_project(tmp_path / "p"))}
    assert {"ALARM_TAG", "ALARM_MEMBER", "ALARM_COND", "ALARM_SEV", "ALARM_MSG"} <= codes
    cj = tmp_path / "p" / "controller.json"
    d = json.loads(cj.read_text(encoding="utf-8"))
    d["processor_type"] = "1756-L73"
    cj.write_text(json.dumps(d), encoding="utf-8")
    assert "TAGALARM_UNSUPPORTED" in {f.code for f in validate(load_project(tmp_path / "p"))}


def _balanced(text: str) -> bool:
    return text.count("{") == text.count("}") and text.count("(") == text.count(")")


def test_hmi_build(tmp_path):
    proj = load_project(DEMO)
    spec = load_hmi_spec(proj)
    assert spec is not None and spec.home_screen == "Overview" and "UDT_Motor" in spec.faceplates
    fp = spec.faceplates["UDT_Motor"]
    kinds = {(r.member, r.type) for r in fp.rows}
    assert ("Cmd_Start", "button") in kinds and ("Sts_Fault", "indicator") in kinds
    assert ("Cfg_FaultDelay_ms", "numeric_input") in kinds and ("Sts_RunHours", "numeric") in kinds
    written = build_viewdesigner(proj, spec, tmp_path / "hmi")
    assert not (tmp_path / "hmi" / "ConveyorDemo_HMI_1_AddOnGraphics").exists()
    rel = {str(Path(w).relative_to(tmp_path / "hmi" / "ConveyorDemo_HMI")).replace("\\", "/") for w in written}
    assert {"ViewApplication.hmi", "User-Defined Screens/Overview.hmi", "User-Defined Screens/Settings.hmi",
            "Assets/Add-On Graphics/AOG_UDT_Motor.hmi", "Navigation Menu/Overview.hmi"} <= rel
    base = tmp_path / "hmi" / "ConveyorDemo_HMI"
    va = (base / "ViewApplication.hmi").read_text(encoding="utf-8")
    assert 'HomeScreen := "Overview";' in va and "ViewProject ConveyorDemo_HMI" in va
    ov = (base / "User-Defined Screens" / "Overview.hmi").read_text(encoding="utf-8")
    assert ov.startswith("namespace ViewDesigner;") and "Screen Overview {" in ov and _balanced(ov)
    assert "using ViewDesigner::AOG;" in ov          # required to resolve user Add-On Graphics (verified by import)
    assert '"::LGX.I_ESTOP_OK"' in ov and 'TagInstance := "::LGX.HMI_Conveyor01"' in ov
    assert 'screenName := "Navigation Menu\\AlarmSummary";' in ov
    assert 'screenName := "User-Defined Screens\\Settings";' in ov
    assert all(l.rstrip().endswith((";", "{", "}", ")", "*/")) or not l.strip() for l in ov.splitlines()), "every statement ends with ;"
    aog = (base / "Assets" / "Add-On Graphics" / "AOG_UDT_Motor.hmi").read_text(encoding="utf-8")
    assert aog.startswith("namespace ViewDesigner::AOG;") and "AddOnGraphic AOG_UDT_Motor {" in aog and _balanced(aog)
    assert '"TagInstance.Sts_Run"' in aog and 'DataType := "::LGX.UDT_Motor";' in aog
    assert "ForceAnimations" not in aog and "ForceAnimations" not in ov
    assert "StateTable StateTable {" not in ov and "StateTable StateTable_" in ov
    assert "TagName" not in ov and '^Tag := "::LGX.Sys_AlarmAck";' in ov
    assert "MinValue" not in (base / "User-Defined Screens" / "Settings.hmi").read_text(encoding="utf-8")
    sc = (base / "Navigation Menu" / "Overview.hmi").read_text(encoding="utf-8")
    assert 'TargetScreenName := "User-Defined Screens\\Overview";' in sc


def test_hmi_validation(tmp_path):
    import json
    import shutil
    shutil.copytree(DEMO, tmp_path / "p")
    hj = tmp_path / "p" / "hmi" / "hmi.json"
    d = json.loads(hj.read_text(encoding="utf-8"))
    d["home_screen"] = "Missing"
    d["screens"][0]["widgets"] += [
        {"type": "indicator", "tag": "NoSuchTag"},
        {"type": "numeric", "tag": "HMI_Conveyor01.Nope"},
        {"type": "button", "tag": "HMI_Conveyor01.Sts_RunHours"},
        {"type": "nav_button", "text": "x", "screen": "Ghost"},
    ]
    hj.write_text(json.dumps(d), encoding="utf-8")
    codes = {f.code for f in validate(load_project(tmp_path / "p"))}
    assert {"HMI_HOME", "HMI_TAG", "HMI_MEMBER", "HMI_TYPE", "HMI_NAV"} <= codes


def test_hmi_docs(tmp_path):
    proj = load_project(DEMO)
    files = write_hmi_docs(proj, tmp_path)
    md = files[0].read_text(encoding="utf-8")
    assert "## HMI_Conveyor01 : UDT_Motor" in md and "HMI writes" in md and "ESTOP_Active" in md
    assert files[1].name == "ALARMS.csv" and "Conveyor01_Fault" in files[1].read_text(encoding="utf-8")
