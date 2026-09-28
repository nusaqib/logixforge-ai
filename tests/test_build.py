import xml.etree.ElementTree as ET
from pathlib import Path

from logixforge.l5x.reader import export_project_dir, read_l5x
from logixforge.l5x.writer import build_partial_tree, serialize, write_l5x
from logixforge.project import load_project
from logixforge.validate import has_errors, validate

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "examples" / "conveyor-demo"


def test_demo_loads_and_validates():
    proj = load_project(DEMO)
    findings = validate(proj)
    assert not has_errors(findings), "\n".join(str(f) for f in findings if f.level == "error")
    assert [p.name for p in proj.programs] == ["P_Conveyor"]
    assert {r.name for r in proj.programs[0].routines} == {"MainRoutine", "R_Inputs", "R_Conveyor", "R_Alarms", "R_Outputs"}


def test_build_full_l5x(tmp_path):
    proj = load_project(DEMO)
    out = write_l5x(proj, str(tmp_path / "demo.L5X"))
    text = Path(out).read_text(encoding="utf-8")
    assert text.startswith('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>')
    assert "<![CDATA[XIC(I_PB_Start)OTE(PB_Start);]]>" in text
    root = ET.parse(out).getroot()
    assert root.tag == "RSLogix5000Content" and root.get("TargetType") == "Controller"
    ctl = root.find("Controller")
    order = [c.tag for c in ctl if c.tag in {"DataTypes", "Modules", "AddOnInstructionDefinitions", "Tags", "Programs", "Tasks"}]
    assert order == ["DataTypes", "Modules", "AddOnInstructionDefinitions", "Tags", "Programs", "Tasks"]
    assert ctl.find("Modules/Module[@Name='Local']") is None      # Studio creates it; emitting it collides
    assert ctl.find("Programs/Program[@Name='P_Conveyor']/Routines/Routine[@Name='R_Alarms']/STContent") is not None
    aoi = ctl.find("AddOnInstructionDefinitions/AddOnInstructionDefinition[@Name='AOI_Motor']")
    assert aoi.find("Parameters/Parameter[@Name='EnableIn']") is not None
    assert aoi.find("Routines/Routine[@Name='Logic']/RLLContent/Rung") is not None
    hmi = ctl.find("Tags/Tag[@Name='HMI_Conveyor01']")
    assert hmi.get("Radix") is None                                  # structured tags carry no Radix
    assert hmi.find("Data[@Format='Decorated']/Structure/DataValueMember[@Name='Cfg_FaultDelay_ms']").get("Value") == "2000"
    assert hmi.find("Data[@Format='Decorated']/Structure/DataValueMember[@Name='Sts_RunHours']").get("Radix") == "Float"
    assert ctl.find("Programs/Program/Tags/Tag[@Name='T_HeartBeat']").get("Radix") is None
    assert aoi.find("LocalTags/LocalTag[@Name='T_Fault']").get("Radix") is None
    assert ctl.find("RedundancyInfo").get("IOMemoryPadPercentage") is None


def test_partial_routine():
    proj = load_project(DEMO)
    tree = build_partial_tree(proj, "Routine", "R_Conveyor", program="P_Conveyor")
    root = tree.getroot()
    assert root.get("TargetType") == "Routine" and root.get("ContainsContext") == "true"
    assert root.find("Controller").get("Use") == "Context"
    assert root.find("Controller/Programs/Program").get("Use") == "Context"
    assert root.find("Controller/Programs/Program/Routines/Routine").get("Use") == "Target"
    assert "<![CDATA[" in serialize(tree)


def test_round_trip(tmp_path):
    proj = load_project(DEMO)
    l5x = write_l5x(proj, str(tmp_path / "demo.L5X"))
    back = read_l5x(l5x)
    assert back.controller.name == "ConveyorDemo"
    assert [r.text for r in back.programs[0].routines[2].rungs] == [r.text for r in proj.programs[0].routines[2].rungs]
    spec_dir = export_project_dir(back, tmp_path / "spec")
    again = load_project(spec_dir)
    assert not has_errors(validate(again))
    assert {t.name for t in again.tags} == {t.name for t in proj.tags}


def test_validator_catches_errors(tmp_path):
    import json
    import shutil
    shutil.copytree(DEMO, tmp_path / "p")
    (tmp_path / "p" / "programs" / "P_Conveyor" / "routines" / "R_Bad.rll").write_text(
        "XIC(A)OTE(B)\n\nTON(T1,?);\nFOO(x);\n", encoding="utf-8")
    (tmp_path / "p" / "tags" / "bad.json").write_text(json.dumps([
        {"name": "XIC", "data_type": "BOOL"}, {"name": "Bad__Name", "data_type": "NOPE"}]), encoding="utf-8")
    try:
        load_project(tmp_path / "p")
        assert False, "expected SpecError for unterminated rung"
    except Exception as e:
        assert "not terminated" in str(e)
    (tmp_path / "p" / "programs" / "P_Conveyor" / "routines" / "R_Bad.rll").write_text(
        "XIC(A)OTE(B);\n\nTON(T1,?);\n\nFOO(x);\n", encoding="utf-8")
    codes = {f.code for f in validate(load_project(tmp_path / "p"))}
    assert {"OPERAND_COUNT", "UNKNOWN_INSTR", "NAME_RESERVED", "NAME_DBL_US", "UNKNOWN_TYPE", "ROUTINE_UNCALLED"} <= codes


def test_controller_attrs_for_l8x_and_desc_limit(tmp_path):
    import json
    import shutil
    proj = load_project(DEMO)
    text = serialize(__import__("logixforge.l5x.writer", fromlist=["build_tree"]).build_tree(proj))
    assert "ShareUnusedTimeSlice" not in text          # 1756-L83E rejects it
    shutil.copytree(DEMO, tmp_path / "p")
    cj = tmp_path / "p" / "controller.json"
    d = json.loads(cj.read_text(encoding="utf-8"))
    d["processor_type"] = "1756-L73"
    d["description"] = "x" * 129
    cj.write_text(json.dumps(d), encoding="utf-8")
    p2 = load_project(tmp_path / "p")
    text2 = serialize(__import__("logixforge.l5x.writer", fromlist=["build_tree"]).build_tree(p2))
    assert 'ShareUnusedTimeSlice="1"' in text2 and 'IOMemoryPadPercentage="90"' in text2
    assert any(f.code == "DESC_LEN" and f.level == "error" for f in validate(p2))


def test_decorated_arrays_and_timer_preset(tmp_path):
    import json
    import shutil
    shutil.copytree(DEMO, tmp_path / "p")
    (tmp_path / "p" / "tags" / "extra.json").write_text(json.dumps([
        {"name": "Arr", "data_type": "DINT", "dimensions": "4", "value": [1, 2, 3, 4], "description": "d"},
        {"name": "T_Preset", "data_type": "TIMER", "value": {"PRE": 500}, "description": "d"},
        {"name": "Motors", "data_type": "UDT_Motor", "dimensions": "2",
         "value": [{"Cfg_FaultDelay_ms": 1}, {"Cfg_FaultDelay_ms": 2}], "description": "d"},
    ]), encoding="utf-8")
    proj = load_project(tmp_path / "p")
    assert not has_errors(validate(proj))
    out = write_l5x(proj, str(tmp_path / "x.L5X"))
    ctl = ET.parse(out).getroot().find("Controller")
    arr = ctl.find("Tags/Tag[@Name='Arr']/Data/Array")
    assert arr.get("Radix") == "Decimal" and [e.get("Value") for e in arr] == ["1", "2", "3", "4"]
    assert ctl.find("Tags/Tag[@Name='T_Preset']/Data/Structure/DataValueMember[@Name='PRE']").get("Value") == "500"
    m2 = ctl.find("Tags/Tag[@Name='Motors']/Data/Array/Element[@Index='[1]']/Structure/DataValueMember[@Name='Cfg_FaultDelay_ms']")
    assert m2.get("Value") == "2"
    assert read_l5x(out).find_program("P_Conveyor") is not None
