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


def test_st_comments_module_types_handlers(tmp_path):
    import json
    import shutil
    shutil.copytree(DEMO, tmp_path / "p")
    (tmp_path / "p" / "programs" / "P_Conveyor" / "routines" / "R_Cmt.st").write_text(
        "/* for the record: if this was counted, FOR/IF would mismatch */\n(* while *) // repeat\n"
        "IF Sim_Mode THEN Alarm_Any := 1; ELSIF ESTOP_OK THEN Alarm_Any := 0; ELSE Alarm_Any := 0; END_IF;\n"
        "FOR i := 0 TO 3 DO Alarm_Any := 0; END_FOR;\n", encoding="utf-8")
    (tmp_path / "p" / "tags" / "mod.json").write_text(json.dumps([
        {"name": "Drive1_Out", "data_type": "_000A:SD4840E2_4342D302:O:0", "description": "module-defined type"},
        {"name": "i", "data_type": "DINT", "description": "loop index"}]), encoding="utf-8")
    pu = tmp_path / "p" / "programs" / "P_PowerUp"
    (pu / "routines").mkdir(parents=True)
    (pu / "program.json").write_text(json.dumps({"name": "P_PowerUp", "main_routine": "MainRoutine"}), encoding="utf-8")
    (pu / "routines" / "MainRoutine.rll").write_text("//! power-up handler\nNOP();\n", encoding="utf-8")
    cj = tmp_path / "p" / "controller.json"
    d = json.loads(cj.read_text(encoding="utf-8"))
    d["power_loss_program"] = "P_PowerUp"
    cj.write_text(json.dumps(d), encoding="utf-8")
    proj = load_project(tmp_path / "p")
    codes = {f.code for f in validate(proj)}
    assert "ST_BLOCK" not in codes and "UNKNOWN_TYPE" not in codes and "UNSCHEDULED" not in codes
    text = Path(write_l5x(proj, str(tmp_path / "x.L5X"))).read_text(encoding="utf-8")
    assert 'PowerLossProgram="P_PowerUp"' in text
    assert read_l5x(tmp_path / "x.L5X").controller.power_loss_program == "P_PowerUp"


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


def test_fbd_timer_data_defaults_and_incomplete_structures(tmp_path):
    """BACKLOG 19: FBD_TIMER members rendered as Studio exports them (EnableIn = 1); a structure with an
    unknown member type gets no Data element instead of an incomplete one."""
    import json
    import shutil
    shutil.copytree(DEMO, tmp_path / "p")
    (tmp_path / "p" / "datatypes" / "UDT_Seq.json").write_text(json.dumps({
        "name": "UDT_Seq", "description": "d", "members": [
            {"name": "Step_Val", "data_type": "DINT", "description": "d"},
            {"name": "Pulse_Tmr", "data_type": "FBD_TIMER", "description": "d"}]}), encoding="utf-8")
    (tmp_path / "p" / "datatypes" / "UDT_Odd.json").write_text(json.dumps({
        "name": "UDT_Odd", "description": "d", "members": [
            {"name": "A", "data_type": "DINT", "description": "d"},
            {"name": "Pid", "data_type": "PID_ENHANCED", "description": "d"}]}), encoding="utf-8")
    (tmp_path / "p" / "tags" / "extra.json").write_text(json.dumps([
        {"name": "Seq", "data_type": "UDT_Seq", "value": {"Step_Val": 3, "Pulse_Tmr": {"PRE": 250}}, "description": "d"},
        {"name": "Odd", "data_type": "UDT_Odd", "value": {"A": 1}, "description": "d"},
        {"name": "OS", "data_type": "FBD_ONESHOT", "value": {}, "description": "d"},
    ]), encoding="utf-8")
    proj = load_project(tmp_path / "p")
    out = write_l5x(proj, str(tmp_path / "x.L5X"))
    ctl = ET.parse(out).getroot().find("Controller")
    tmr = ctl.find("Tags/Tag[@Name='Seq']/Data/Structure/StructureMember[@Name='Pulse_Tmr']")
    members = {m.get("Name"): m.get("Value") for m in tmr}
    assert members["EnableIn"] == "1" and members["PRE"] == "250" and members["PresetInv"] == "0"
    assert list(members) == ["EnableIn", "TimerEnable", "PRE", "Reset", "EnableOut", "ACC", "EN", "TT", "DN", "Status", "InstructFault", "PresetInv"]
    assert ctl.find("Tags/Tag[@Name='Odd']/Data") is None          # incomplete structure: no Data at all
    assert ctl.find("Tags/Tag[@Name='OS']/Data/Structure/DataValueMember[@Name='EnableIn']").get("Value") == "1"


def test_aoi_default_strings_written_bare(tmp_path):
    """BACKLOG 18: a decompiled AOI carries defaults as strings; BOOL/DINT defaults must not be quoted."""
    import json
    import shutil
    shutil.copytree(DEMO, tmp_path / "p")
    aoi = tmp_path / "p" / "aois" / "AOI_Motor" / "aoi.json"
    d = json.loads(aoi.read_text(encoding="utf-8"))
    for prm in d["parameters"]:
        if prm["name"] == "Start":
            prm["default"] = "0"
        if prm["name"] == "FaultDelay":
            prm["default"] = "2000"
    aoi.write_text(json.dumps(d), encoding="utf-8")
    out = write_l5x(load_project(tmp_path / "p"), str(tmp_path / "x.L5X"))
    text = Path(out).read_text(encoding="utf-8")
    assert "<![CDATA['0']]>" not in text and "<![CDATA['2000']]>" not in text
    assert "<DefaultData Format=\"L5K\"><![CDATA[2000]]></DefaultData>" in text


def test_validator_value_range(tmp_path):
    """BACKLOG 20: initial values that do not fit the member type are errors (Studio keeps 0 silently)."""
    import json
    import shutil
    shutil.copytree(DEMO, tmp_path / "p")
    (tmp_path / "p" / "datatypes" / "UDT_Sp.json").write_text(json.dumps({
        "name": "UDT_Sp", "description": "d", "members": [{"name": "Deadband_SP", "data_type": "INT", "description": "ms"}]}), encoding="utf-8")
    (tmp_path / "p" / "tags" / "extra.json").write_text(json.dumps([
        {"name": "Sp", "data_type": "UDT_Sp", "value": {"Deadband_SP": 60000}, "description": "d"},
        {"name": "Ok", "data_type": "INT", "value": 30000, "description": "d"},
        {"name": "Big", "data_type": "SINT", "dimensions": "2", "value": [1, 300], "description": "d"},
    ]), encoding="utf-8")
    codes = [(f.code, f.where) for f in validate(load_project(tmp_path / "p")) if f.code == "VALUE_RANGE"]
    assert ("VALUE_RANGE", "controller tag Sp") in codes and ("VALUE_RANGE", "controller tag Big") in codes
    assert not any(w == "controller tag Ok" for _, w in codes)
