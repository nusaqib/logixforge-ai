import pytest

from logixforge.rll import RungSyntaxError, instruction_names, operand_tags, parse_rung


def test_simple_rung():
    p = parse_rung("XIC(Start)XIO(Stop)OTE(Run);")
    assert instruction_names("XIC(Start)XIO(Stop)OTE(Run);") == ["XIC", "XIO", "OTE"]
    assert operand_tags("XIC(Start)XIO(Stop)OTE(Run);") == ["Start", "Stop", "Run"]
    assert len(p.elements) == 3


def test_branch():
    t = "XIC(Auto)[XIC(PB_Start),XIC(Run)]XIO(PB_Stop)OTE(Run);"
    assert instruction_names(t) == ["XIC", "XIC", "XIC", "XIO", "OTE"]


def test_nested_branch_and_timer():
    t = "[XIC(A)[XIC(B),XIC(C)],XIC(D)]TON(T1,?,?);"
    assert instruction_names(t) == ["XIC", "XIC", "XIC", "XIC", "TON"]
    assert "T1" in operand_tags(t) and "?" not in operand_tags(t)


def test_cpt_expression_tags():
    t = "CPT(Result,(A+B)*2/Scale[3]);"
    tags = operand_tags(t)
    assert tags[0] == "Result" and "A" in tags and "Scale[3]" in tags


def test_aoi_call():
    p = parse_rung("AOI_Motor(M1,Start,Stop,Fb,Rst,Run,Flt);")
    ins = list(p.walk())[0]
    assert ins.is_aoi and ins.name == "AOI_Motor" and len(ins.operands) == 7


def test_literals_dropped():
    assert operand_tags("EQU(Mode,2)MOV(16#FF,Mask)OTE(Out);") == ["Mode", "Mask", "Out"]


@pytest.mark.parametrize("bad", ["XIC(A)OTE(B)", "XIC(A", "XIC(A)]OTE(B);", "[XIC(A),XIC(B)OTE(C);", "XIC A;"])
def test_syntax_errors(bad):
    with pytest.raises(RungSyntaxError):
        parse_rung(bad)
