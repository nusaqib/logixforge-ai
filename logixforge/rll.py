"""Ladder (RLL) neutral-text parsing and instruction catalogue.

Studio 5000 rung text grammar (subset that covers production code):

    rung     := element* ';'
    element  := INSTR '(' operands ')' | branch
    branch   := '[' level (',' level)* ']'
    level    := element*
    operands := operand (',' operand)*      -- operand may be '?' (auto-fill) or blank

Examples:
    XIC(Start)XIO(Stop)OTE(Run);
    XIC(Auto)[XIC(PB_Start),XIC(Run)]XIO(PB_Stop)OTE(Run);
    TON(T_Delay,?,?);
    AOI_Motor(Motor01,Motor01_Cmd,Local:2:I.Data.0);
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Union

# name -> (min operands, max operands or -1 for variadic, category)
INSTRUCTIONS: dict[str, tuple[int, int, str]] = {
    # bit
    "XIC": (1, 1, "bit"), "XIO": (1, 1, "bit"), "OTE": (1, 1, "bit"), "OTL": (1, 1, "bit"), "OTU": (1, 1, "bit"),
    "ONS": (1, 1, "bit"), "OSR": (2, 2, "bit"), "OSF": (2, 2, "bit"), "OSRI": (1, 1, "bit"), "OSFI": (1, 1, "bit"),
    # timer/counter
    "TON": (3, 3, "timer"), "TOF": (3, 3, "timer"), "RTO": (3, 3, "timer"), "CTU": (3, 3, "counter"),
    "CTD": (3, 3, "counter"), "RES": (1, 1, "timer"), "TONR": (1, 1, "timer"), "TOFR": (1, 1, "timer"),
    "RTOR": (1, 1, "timer"), "CTUD": (1, 1, "counter"),
    # compare
    "CMP": (1, 1, "compare"), "EQU": (2, 2, "compare"), "NEQ": (2, 2, "compare"), "LES": (2, 2, "compare"),
    "LEQ": (2, 2, "compare"), "GRT": (2, 2, "compare"), "GEQ": (2, 2, "compare"), "LIM": (3, 3, "compare"),
    "MEQ": (3, 3, "compare"),
    # math
    "CPT": (2, 2, "math"), "ADD": (3, 3, "math"), "SUB": (3, 3, "math"), "MUL": (3, 3, "math"), "DIV": (3, 3, "math"),
    "MOD": (3, 3, "math"), "SQR": (2, 2, "math"), "NEG": (2, 2, "math"), "ABS": (2, 2, "math"), "SQRT": (2, 2, "math"),
    "XPY": (3, 3, "math"), "LN": (2, 2, "math"), "LOG": (2, 2, "math"), "SIN": (2, 2, "math"), "COS": (2, 2, "math"),
    "TAN": (2, 2, "math"), "ASN": (2, 2, "math"), "ACS": (2, 2, "math"), "ATN": (2, 2, "math"), "DEG": (2, 2, "math"),
    "RAD": (2, 2, "math"), "TRN": (2, 2, "math"), "TRUNC": (2, 2, "math"),
    # move/logical
    "MOV": (2, 2, "move"), "MVM": (3, 3, "move"), "BTD": (5, 5, "move"), "CLR": (1, 1, "move"), "SWPB": (3, 3, "move"),
    "AND": (3, 3, "move"), "OR": (3, 3, "move"), "XOR": (3, 3, "move"), "NOT": (2, 2, "move"), "BAND": (3, -1, "move"),
    "BOR": (3, -1, "move"), "BXOR": (3, -1, "move"), "BNOT": (2, 2, "move"),
    # array/file
    "FAL": (6, 6, "file"), "FSC": (6, 6, "file"), "COP": (3, 3, "file"), "CPS": (3, 3, "file"), "FLL": (3, 3, "file"),
    "AVE": (5, 5, "file"), "SRT": (4, 4, "file"), "STD": (5, 5, "file"), "SIZE": (3, 3, "file"),
    "BSL": (4, 4, "shift"), "BSR": (4, 4, "shift"), "FFL": (4, 4, "shift"), "FFU": (4, 4, "shift"),
    "LFL": (4, 4, "shift"), "LFU": (4, 4, "shift"),
    "SQI": (5, 5, "seq"), "SQO": (5, 5, "seq"), "SQL": (4, 4, "seq"),
    # program control
    "JMP": (1, 1, "control"), "LBL": (1, 1, "control"), "JSR": (1, -1, "control"), "JXR": (1, -1, "control"),
    "RET": (0, -1, "control"), "SBR": (0, -1, "control"), "TND": (0, 0, "control"), "MCR": (0, 0, "control"),
    "UID": (0, 0, "control"), "UIE": (0, 0, "control"), "AFI": (0, 0, "control"), "NOP": (0, 0, "control"),
    "EOT": (0, 0, "control"), "SFR": (2, 2, "control"), "SFP": (2, 2, "control"), "EVENT": (1, 1, "control"),
    "FOR": (5, 5, "control"), "BRK": (0, 0, "control"),
    # special / IO / comms / process
    "MSG": (1, 1, "comm"), "GSV": (4, 4, "sys"), "SSV": (4, 4, "sys"), "IOT": (1, 1, "io"), "PID": (7, 7, "process"),
    "PIDE": (1, 1, "process"), "FBC": (7, 7, "file"), "DDT": (7, 7, "file"), "DTR": (3, 3, "file"),
    "ALMD": (6, 6, "alarm"), "ALMA": (6, 6, "alarm"),
    # string / ascii
    "DTOS": (2, 2, "string"), "STOD": (2, 2, "string"), "RTOS": (2, 2, "string"), "STOR": (2, 2, "string"),
    "UPPER": (2, 2, "string"), "LOWER": (2, 2, "string"), "CONCAT": (3, 3, "string"), "DELETE": (4, 4, "string"),
    "FIND": (4, 4, "string"), "INSERT": (4, 4, "string"), "MID": (4, 4, "string"),
    "AWA": (4, 4, "ascii"), "AWT": (4, 4, "ascii"), "ARD": (4, 4, "ascii"), "ARL": (4, 4, "ascii"),
    "ABL": (2, 2, "ascii"), "ACB": (2, 2, "ascii"), "ACL": (3, 3, "ascii"), "AHL": (5, 5, "ascii"),
    # motion (operand counts vary; variadic)
    "MSO": (2, -1, "motion"), "MSF": (2, -1, "motion"), "MAS": (2, -1, "motion"), "MAH": (2, -1, "motion"),
    "MAJ": (2, -1, "motion"), "MAM": (2, -1, "motion"), "MAG": (2, -1, "motion"), "MCD": (2, -1, "motion"),
    "MRP": (2, -1, "motion"), "MAFR": (2, -1, "motion"), "MDO": (2, -1, "motion"), "MDF": (2, -1, "motion"),
    "MGS": (2, -1, "motion"), "MGSD": (2, -1, "motion"), "MGSR": (2, -1, "motion"), "MGSP": (2, -1, "motion"),
    "MAW": (2, -1, "motion"), "MDW": (2, -1, "motion"), "MAR": (2, -1, "motion"), "MDR": (2, -1, "motion"),
    "MAOC": (2, -1, "motion"), "MDOC": (2, -1, "motion"), "MAPC": (2, -1, "motion"), "MATC": (2, -1, "motion"),
    "MCCP": (2, -1, "motion"), "MCCM": (2, -1, "motion"), "MCLM": (2, -1, "motion"), "MCS": (2, -1, "motion"),
    "MCSD": (2, -1, "motion"), "MCSR": (2, -1, "motion"), "MCT": (2, -1, "motion"), "MCTP": (2, -1, "motion"),
    "MDAC": (2, -1, "motion"), "MDCC": (2, -1, "motion"),
    # safety (GuardLogix) - variadic, validated by Studio 5000
    "SMAT": (1, -1, "safety"), "ESTOP": (1, -1, "safety"), "LC": (1, -1, "safety"), "DCS": (1, -1, "safety"),
    "DCST": (1, -1, "safety"), "DCSRT": (1, -1, "safety"), "DCM": (1, -1, "safety"), "DCSTL": (1, -1, "safety"),
    "DCSTM": (1, -1, "safety"), "DCA": (1, -1, "safety"), "SMAT_": (0, 0, "x"), "RIN": (1, -1, "safety"),
    "ROUT": (1, -1, "safety"), "FPMS": (1, -1, "safety"), "ENPEN": (1, -1, "safety"), "TSAM": (1, -1, "safety"),
    "TSSM": (1, -1, "safety"), "SSV_": (0, 0, "x"), "CROUT": (1, -1, "safety"), "THRSe": (1, -1, "safety"),
    "MMVC": (1, -1, "safety"), "SFX": (1, -1, "safety"), "SMAT__": (0, 0, "x"), "CBCM": (1, -1, "safety"),
    "CBIM": (1, -1, "safety"), "CBSSM": (1, -1, "safety"), "CPM": (1, -1, "safety"), "EPMS": (1, -1, "safety"),
    "SOS": (1, -1, "safety"), "SS1": (1, -1, "safety"), "SS2": (1, -1, "safety"), "SLS": (1, -1, "safety"),
    "SDI": (1, -1, "safety"), "SBC": (1, -1, "safety"), "SOR": (1, -1, "safety"), "SFI": (1, -1, "safety"),
    "SFT": (1, -1, "safety"), "STO": (1, -1, "safety"),
}
# Logix v36+ renamed mnemonics in rung text (imports still accept the old ones and convert them)
INSTRUCTIONS.update({
    "MOVE": (2, 2, "move"), "EQ": (2, 2, "compare"), "NE": (2, 2, "compare"), "GT": (2, 2, "compare"),
    "GE": (2, 2, "compare"), "LT": (2, 2, "compare"), "LE": (2, 2, "compare"), "LIMIT": (3, 3, "compare"),
})
V36_ALIASES = {"MOV": "MOVE", "EQU": "EQ", "NEQ": "NE", "GRT": "GT", "GEQ": "GE", "LES": "LT", "LEQ": "LE", "LIM": "LIMIT"}
INSTRUCTIONS = {k.upper(): v for k, v in INSTRUCTIONS.items() if not k.endswith("_")}

# Instruction names and ST keywords cannot be used as tag names
RESERVED_WORDS = set(INSTRUCTIONS) | {
    "ABS", "ACOS", "AND", "ASIN", "ATAN", "BY", "CASE", "COS", "DO", "ELSE", "ELSIF", "END_CASE", "END_FOR",
    "END_IF", "END_REPEAT", "END_WHILE", "EXIT", "FOR", "GOTO", "IF", "LN", "LOG", "MOD", "NOT", "OF", "OR",
    "REPEAT", "RETURN", "SIN", "SQRT", "TAN", "THEN", "TO", "TRUNC", "UNTIL", "WHILE", "XOR",
}

NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


@dataclass
class Instr:
    name: str
    operands: list[str] = field(default_factory=list)
    is_aoi: bool = False


@dataclass
class Branch:
    levels: list[list["Element"]] = field(default_factory=list)


Element = Union[Instr, Branch]


@dataclass
class ParsedRung:
    elements: list[Element] = field(default_factory=list)

    def walk(self):
        """Yield every Instr in scan order (depth-first through branches)."""
        stack: list[Element] = list(reversed(self.elements))
        while stack:
            e = stack.pop()
            if isinstance(e, Instr):
                yield e
            else:
                for level in reversed(e.levels):
                    stack.extend(reversed(level))


class RungSyntaxError(ValueError):
    pass


def _split_operands(s: str) -> list[str]:
    """Split on commas that are not inside parentheses/brackets (CPT expressions, indexes)."""
    out: list[str] = []
    depth = 0
    cur: list[str] = []
    for ch in s:
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth -= 1
        if ch == "," and depth == 0:
            out.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    out.append("".join(cur).strip())
    if out == [""]:
        return []
    return out


def parse_rung(text: str) -> ParsedRung:
    """Parse neutral rung text into a tree. Raises RungSyntaxError."""
    s = text.strip()
    if not s.endswith(";"):
        raise RungSyntaxError("rung text must end with ';'")
    s = s[:-1]
    n = len(s)
    pos = 0

    def parse_elements(stop: set[str]) -> list[Element]:
        nonlocal pos
        elems: list[Element] = []
        while pos < n:
            ch = s[pos]
            if ch.isspace():
                pos += 1
                continue
            if ch in stop:
                return elems
            if ch == "[":
                pos += 1
                levels = [parse_elements({",", "]"})]
                while pos < n and s[pos] == ",":
                    pos += 1
                    levels.append(parse_elements({",", "]"}))
                if pos >= n or s[pos] != "]":
                    raise RungSyntaxError("unterminated branch '['")
                pos += 1
                elems.append(Branch(levels))
                continue
            m = re.match(r"[A-Za-z_][A-Za-z0-9_]*", s[pos:])
            if not m:
                raise RungSyntaxError(f"unexpected character {ch!r} at column {pos}")
            name = m.group(0)
            pos += len(name)
            while pos < n and s[pos].isspace():
                pos += 1
            if pos >= n or s[pos] != "(":
                raise RungSyntaxError(f"instruction {name} missing '('")
            depth = 0
            start = pos
            while pos < n:
                if s[pos] == "(":
                    depth += 1
                elif s[pos] == ")":
                    depth -= 1
                    if depth == 0:
                        break
                pos += 1
            if depth != 0:
                raise RungSyntaxError(f"instruction {name} missing ')'")
            inner = s[start + 1:pos]
            pos += 1
            upper = name.upper()
            known = upper in INSTRUCTIONS
            elems.append(Instr(upper if known else name, _split_operands(inner), not known))
        if stop:
            raise RungSyntaxError("unterminated branch")
        return elems

    return ParsedRung(parse_elements(set()))


def instruction_names(text: str) -> list[str]:
    return [i.name for i in parse_rung(text).walk()]


_LITERAL_RE = re.compile(r"^(-?\d|'|\"|16#|8#|2#)")


def operand_tags(text: str) -> list[str]:
    """Return operand tokens that look like tag references (drops literals and '?')."""
    out: list[str] = []
    for i in parse_rung(text).walk():
        for op in i.operands:
            if not op or op.startswith("?"):
                continue
            if _LITERAL_RE.match(op):
                continue
            if i.name in {"CPT", "CMP", "FAL", "FSC"} and re.search(r"[+\-*/<>=]", op):
                out.extend(t for t in re.findall(r"[A-Za-z_][A-Za-z0-9_:.\[\]]*", op) if t.upper() not in RESERVED_WORDS)
            else:
                out.append(op)
    return out


def base_tag(operand: str) -> str:
    """'Motor[3].Cmd.Start' -> 'Motor';  'Local:2:I.Data.0' -> 'Local:2:I'."""
    m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*(?::\d+:[A-Za-z0-9_]+)?)", operand)
    return m.group(1) if m else operand
