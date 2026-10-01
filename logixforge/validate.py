"""Static validation of a Project (spec or L5X-derived) against Logix rules and house standards.

Returns a list of Finding(level, code, where, message). Levels: error | warning | info.
Errors will fail import or download in Studio 5000; warnings are standards/quality issues.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from .model import ALARM_CONDITIONS, ATOMIC_TYPES, PREDEFINED_TYPES, Project, Tag, is_known_type
from .rll import INSTRUCTIONS, NAME_RE, RESERVED_WORDS, RungSyntaxError, base_tag, operand_tags, parse_rung

IO_TAG_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(:(\d+|[A-Za-z0-9_]+))?:[ICOS]\d?(\.|$)")   # Local:2:I, Rack1:3:O, Drive1:O


@dataclass
class Finding:
    level: str
    code: str
    where: str
    message: str

    def __str__(self) -> str:
        return f"[{self.level.upper():7}] {self.code:12} {self.where}: {self.message}"


class Validator:
    def __init__(self, proj: Project, naming: dict | None = None):
        self.p = proj
        self.f: list[Finding] = []
        self.naming = naming or {}

    # ------------------------------------------------------------ helpers
    def err(self, code, where, msg):
        self.f.append(Finding("error", code, where, msg))

    def warn(self, code, where, msg):
        self.f.append(Finding("warning", code, where, msg))

    def info(self, code, where, msg):
        self.f.append(Finding("info", code, where, msg))

    def check_name(self, name: str, where: str, kind: str = "tag"):
        if not NAME_RE.match(name):
            self.err("NAME_CHARS", where, f"{kind} name {name!r} must start with letter/underscore and use only [A-Za-z0-9_]")
        if len(name) > 40:
            self.err("NAME_LEN", where, f"{kind} name {name!r} exceeds 40 characters")
        if "__" in name:
            self.err("NAME_DBL_US", where, f"{kind} name {name!r} contains consecutive underscores")
        if name.endswith("_"):
            self.err("NAME_TRAIL_US", where, f"{kind} name {name!r} ends with underscore")
        if name.upper() in RESERVED_WORDS:
            self.err("NAME_RESERVED", where, f"{kind} name {name!r} is a reserved instruction/keyword")
        pat = self.naming.get(kind)
        if pat and not re.match(pat, name) and not any(re.match(x, name) for x in self.naming.get("name_exempt", [])):
            self.warn("NAME_STYLE", where, f"{kind} name {name!r} does not match house pattern {pat}")

    def check_suffix(self, name: str, data_type: str, dimensions: str, where: str):
        """Site suffix rules (naming.json 'suffixes': {BOOL:[..], REAL:[..], TIMER:[..], array:[..]}, 'exempt': [regex])."""
        rules = self.naming.get("suffixes")
        if not rules or not data_type:
            return
        if any(re.match(x, name) for x in self.naming.get("exempt", [])):
            return
        key = "array" if dimensions else data_type
        allowed = rules.get(key)
        if dimensions:
            allowed = (allowed or []) + rules.get(data_type, [])
        if not allowed:
            return
        if not any(name.endswith(s) or name == s.lstrip("_") for s in allowed):
            self.warn("NAME_SUFFIX", where, f"{key} name {name!r} should end with one of {' '.join(allowed)}")

    # ------------------------------------------------------------ rules
    def run(self) -> list[Finding]:
        self.check_controller()
        self.check_data_types()
        self.check_aois()
        self.check_tags(self.p.tags, "controller")
        self.check_programs()
        self.check_tasks()
        self.check_alarms()
        self.check_hmi()
        self.check_docs()
        return self.f

    MAX_DESC = 128

    def check_desc(self, desc: str, where: str, hard: bool = False):
        if desc and len(desc) > self.MAX_DESC:
            msg = f"description is {len(desc)} chars; Studio 5000 limit is {self.MAX_DESC}"
            (self.err if hard else self.warn)("DESC_LEN", where, msg)

    def check_controller(self):
        c = self.p.controller
        self.check_name(c.name, "controller", "controller")
        self.check_desc(c.description, "controller", hard=True)
        if not c.processor_type:
            self.err("CTL_TYPE", "controller", "processor_type is required")

    def check_data_types(self):
        seen = set()
        known = self.p.data_type_names()
        for d in self.p.data_types:
            w = f"datatype {d.name}"
            self.check_name(d.name, w, "udt")
            self.check_desc(d.description, w)
            if d.name.lower() in seen:
                self.err("DUP_UDT", w, "duplicate data type name")
            seen.add(d.name.lower())
            if not d.members:
                self.err("UDT_EMPTY", w, "data type has no members")
            mseen = set()
            bools = 0
            for m in d.members:
                mw = f"{w}.{m.name}"
                self.check_name(m.name, mw, "member")
                if m.name.lower() in mseen:
                    self.err("DUP_MEMBER", mw, "duplicate member name")
                mseen.add(m.name.lower())
                if not is_known_type(m.data_type, known):
                    self.err("UNKNOWN_TYPE", mw, f"unknown data type {m.data_type!r}")
                if m.data_type == d.name:
                    self.err("UDT_RECURSIVE", mw, "data type cannot contain itself")
                if m.data_type == "BOOL" and m.dimension and m.dimension % 32:
                    self.err("BOOL_ARRAY_UDT", mw, "BOOL arrays in UDTs must be dimensioned in multiples of 32 (prefer DINT bit fields)")
                if m.data_type == "BOOL":
                    bools += 1
                if not m.description:
                    self.warn("NO_DESC", mw, "member has no description")
                self.check_suffix(m.name, m.data_type, str(m.dimension or ""), mw)
            if bools > 8 and len(d.members) < 2 * bools:
                self.info("UDT_LAYOUT", w, "many BOOL members: consider grouping BOOLs together to reduce padding")

    def check_aois(self):
        for a in self.p.aois:
            w = f"aoi {a.name}"
            self.check_name(a.name, w, "aoi")
            self.check_desc(a.description, w)
            if not a.routines or not any(r.name == "Logic" for r in a.routines):
                self.err("AOI_NO_LOGIC", w, "AOI needs a routine named 'Logic'")
            names = set()
            for prm in a.parameters:
                pw = f"{w}.{prm.name}"
                self.check_name(prm.name, pw, "parameter")
                if prm.name.lower() in names:
                    self.err("DUP_PARAM", pw, "duplicate parameter/local name")
                names.add(prm.name.lower())
                if prm.usage not in {"Input", "Output", "InOut"}:
                    self.err("AOI_USAGE", pw, f"usage must be Input/Output/InOut, got {prm.usage!r}")
                if not is_known_type(prm.data_type, self.p.data_type_names()):
                    self.err("UNKNOWN_TYPE", pw, f"unknown data type {prm.data_type!r}")
                if prm.usage in {"Input", "Output"} and prm.data_type not in ATOMIC_TYPES:
                    self.err("AOI_PARAM_TYPE", pw, "Input/Output parameters must be atomic; use InOut for structures/arrays")
                if not prm.description:
                    self.warn("NO_DESC", pw, "parameter has no description")
            for lt in a.local_tags:
                if lt.name.lower() in names:
                    self.err("DUP_PARAM", f"{w}.{lt.name}", "local tag collides with parameter name")
                names.add(lt.name.lower())
                self.check_name(lt.name, f"{w}.{lt.name}", "local")
            scope_tags = {n for n in names} | {"enablein", "enableout"}
            for r in a.routines:
                self.check_routine(r, f"{w}/{r.name}", scope_tags, set(), aoi_scope=True)

    def check_tags(self, tags: list[Tag], scope: str, aoi_names: set[str] | None = None):
        seen = set()
        known = self.p.data_type_names()
        for t in tags:
            w = f"{scope} tag {t.name}"
            self.check_name(t.name, w, "tag")
            if t.name.lower() in seen:
                self.err("DUP_TAG", w, "duplicate tag name in scope")
            seen.add(t.name.lower())
            if t.alias_for:
                if not (IO_TAG_RE.match(t.alias_for) or base_tag(t.alias_for).lower() in self.all_tag_names(scope)):
                    self.warn("ALIAS_TARGET", w, f"alias target {t.alias_for!r} not found in project (OK if module-defined I/O)")
            else:
                if not t.data_type:
                    self.err("TAG_NO_TYPE", w, "tag has no data_type")
                elif not is_known_type(t.data_type, known):
                    self.err("UNKNOWN_TYPE", w, f"unknown data type {t.data_type!r}")
                if t.data_type == "BOOL" and t.dimensions and int(t.dimensions.split(",")[0]) % 32:
                    self.err("BOOL_ARRAY", w, "BOOL array dimension must be a multiple of 32")
            if not t.description:
                self.warn("NO_DESC", w, "tag has no description")
            self.check_desc(t.description, w)
            if not t.alias_for and t.data_type not in {d.name for d in self.p.data_types} \
                    and t.data_type not in {a.name for a in self.p.aois}:
                self.check_suffix(t.name, t.data_type, t.dimensions, w)
            if scope == "controller" and t.data_type in ATOMIC_TYPES and not t.alias_for and not t.constant:
                pass  # allowed; house rule may prefer program scope (see standards)

    def all_tag_names(self, scope: str) -> set[str]:
        names = self.p.controller_tag_names()
        if scope.startswith("program:"):
            p = self.p.find_program(scope.split(":", 1)[1])
            if p:
                names |= {t.name.lower() for t in p.tags}
        return names

    def check_programs(self):
        seen = set()
        scheduled = {n.lower() for t in self.p.tasks for n in t.programs}
        scheduled |= {x.lower() for x in (self.p.controller.power_loss_program, self.p.controller.major_fault_program) if x}
        for p in self.p.programs:
            w = f"program {p.name}"
            self.check_name(p.name, w, "program")
            self.check_desc(p.description, w)
            if p.name.lower() in seen:
                self.err("DUP_PROGRAM", w, "duplicate program name")
            seen.add(p.name.lower())
            self.check_tags(p.tags, f"program:{p.name}")
            rnames = {r.name.lower() for r in p.routines}
            if p.main_routine.lower() not in rnames:
                self.err("MAIN_ROUTINE", w, f"main routine {p.main_routine!r} not found among routines {sorted(rnames)}")
            if p.fault_routine and p.fault_routine.lower() not in rnames:
                self.err("FAULT_ROUTINE", w, f"fault routine {p.fault_routine!r} not found")
            if p.name.lower() not in scheduled and not p.disabled:
                self.warn("UNSCHEDULED", w, "program is not scheduled in any task")
            scope = self.all_tag_names(f"program:{p.name}")
            called: set[str] = set()
            for r in p.routines:
                self.check_name(r.name, f"{w}/{r.name}", "routine")
                self.check_routine(r, f"{w}/{r.name}", scope, rnames, called=called)
            for r in p.routines:
                if r.name.lower() != p.main_routine.lower() and r.name.lower() != p.fault_routine.lower() \
                        and r.name.lower() not in called:
                    self.warn("ROUTINE_UNCALLED", f"{w}/{r.name}", "routine is never called with JSR from this program")

    def check_routine(self, r, where: str, scope_tags: set[str], routine_names: set[str], aoi_scope=False, called=None):
        if r.kind == "RLL":
            if not r.rungs:
                self.warn("EMPTY_ROUTINE", where, "routine has no rungs")
            for rung in r.rungs:
                rw = f"{where} rung {rung.number}"
                try:
                    parsed = parse_rung(rung.text)
                except RungSyntaxError as e:
                    self.err("RUNG_SYNTAX", rw, f"{e}: {rung.text}")
                    continue
                instrs = list(parsed.walk())
                if not instrs:
                    self.warn("EMPTY_RUNG", rw, "rung has no instructions")
                    continue
                outputs = 0
                for ins in instrs:
                    if ins.is_aoi:
                        if ins.name not in {a.name for a in self.p.aois}:
                            self.err("UNKNOWN_INSTR", rw, f"unknown instruction or AOI {ins.name!r}")
                        else:
                            aoi = next(a for a in self.p.aois if a.name == ins.name)
                            req = 1 + sum(1 for x in aoi.parameters if x.required or x.usage == "InOut")
                            if len(ins.operands) < req:
                                self.err("AOI_OPERANDS", rw, f"{ins.name} needs {req} operands (instance + required params), got {len(ins.operands)}")
                        continue
                    lo, hi, cat = INSTRUCTIONS[ins.name]
                    n = len(ins.operands)
                    if n < lo or (hi != -1 and n > hi):
                        self.err("OPERAND_COUNT", rw, f"{ins.name} expects {lo}{'' if hi == lo else '..' + ('n' if hi == -1 else str(hi))} operands, got {n}")
                    if ins.name in {"OTE"}:
                        outputs += 1
                    if ins.name == "JSR" and called is not None and ins.operands:
                        called.add(ins.operands[0].lower())
                        if routine_names and ins.operands[0].lower() not in routine_names:
                            self.err("JSR_TARGET", rw, f"JSR target routine {ins.operands[0]!r} not found in program")
                    if ins.name in {"OTL", "OTU"}:
                        self.info("LATCH", rw, f"{ins.name} used: ensure a matching unlatch/latch exists and document the retentive intent")
                    if ins.name in {"JMP", "MCR"}:
                        self.warn("FLOW_CTRL", rw, f"{ins.name} used: prefer structured logic; verify no skipped OTEs retain stale state")
                if not rung.comment and len(instrs) > 3:
                    self.info("NO_RUNG_COMMENT", rw, "complex rung without comment")
                # tag existence (skip routine/label names used by flow-control instructions)
                flow_ops = {op for ins in instrs if ins.name in {"JSR", "JXR", "JMP", "LBL", "SBR", "RET", "FOR", "EVENT"}
                            for op in ins.operands[:1]}
                for op in operand_tags(rung.text):
                    if op in flow_ops:
                        continue
                    b = base_tag(op)
                    if IO_TAG_RE.match(op) or b.lower() in scope_tags or b.lower() in {"s", "?"}:
                        continue
                    if aoi_scope:
                        self.err("UNDEF_TAG", rw, f"operand {op!r} is not a parameter or local tag of the AOI")
                    else:
                        self.warn("UNDEF_TAG", rw, f"operand {op!r} not defined in program or controller scope (OK if defined elsewhere)")
        elif r.kind == "ST":
            text = "\n".join(r.st_lines)
            if not text.strip():
                self.warn("EMPTY_ROUTINE", where, "routine has no lines")
            self.check_st(text, where)
            if called is not None:                     # JSR(Routine) / JSR(Routine, n, ...) calls made from ST
                code = re.sub(r"\(\*.*?\*\)|/\*.*?\*/", "", text, flags=re.S)
                code = re.sub(r"//[^\n]*", "", code)                  # line comments only to end of line
                for target in re.findall(r"(?<![A-Za-z0-9_])JSR\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)", code, flags=re.I):
                    called.add(target.lower())
                    if routine_names and target.lower() not in routine_names:
                        self.err("JSR_TARGET", where, f"JSR target routine {target!r} not found in program")
        if r.description == "" and r.kind in {"RLL", "ST"}:
            self.info("NO_DESC", where, "routine has no description ('//!' first line)")

    def check_st(self, text: str, where: str):
        code = re.sub(r"\(\*.*?\*\)", "", text, flags=re.S)
        code = re.sub(r"/\*.*?\*/", "", code, flags=re.S)          # Logix ST also accepts C-style block comments
        code = re.sub(r"//.*", "", code)
        code = re.sub(r"'[^'\n]*'", "''", code)                    # string literals
        pairs = [("IF", "END_IF"), ("CASE", "END_CASE"), ("FOR", "END_FOR"), ("WHILE", "END_WHILE"), ("REPEAT", "END_REPEAT")]
        up = code.upper()
        for a, b in pairs:
            na = len(re.findall(rf"(?<![A-Z_0-9]){a}(?![A-Z_0-9])", up))   # ELSIF/END_IF never match: preceded by S / _
            nb = len(re.findall(rf"(?<![A-Z_0-9]){b}(?![A-Z_0-9])", up))
            if na != nb:
                self.err("ST_BLOCK", where, f"{a}/{b} mismatch ({na} vs {nb})")
        stmts = [s.strip() for s in re.split(r";", code) if s.strip()]
        for s in stmts:
            if re.match(r"^[A-Za-z_][\w\.\[\]:]*\s*=\s*[^=]", s) and ":=" not in s and not re.match(r"^(IF|ELSIF|WHILE|UNTIL|CASE|FOR|OF|ELSE|END)", s.upper()):
                self.warn("ST_ASSIGN", where, f"'=' used where ':=' assignment likely intended: {s[:60]!r}")
        if re.search(r"(?<![A-Z_])(TON|TOF|RTO|CTU|CTD)\s*\(", up):
            self.err("ST_TIMER", where, "ladder timer/counter instructions are not valid in ST; use TONR/TOFR/RTOR/CTUD with FBD_TIMER/FBD_COUNTER")

    def check_tasks(self):
        if not self.p.tasks:
            self.err("NO_TASKS", "tasks", "at least one task is required")
        cont = [t for t in self.p.tasks if t.kind == "CONTINUOUS"]
        if len(cont) > 1:
            self.err("MULTI_CONT", "tasks", "only one continuous task is allowed")
        prog_names = {p.name.lower() for p in self.p.programs}
        seen_prog = set()
        for t in self.p.tasks:
            w = f"task {t.name}"
            self.check_name(t.name, w, "task")
            if t.kind not in {"CONTINUOUS", "PERIODIC", "EVENT"}:
                self.err("TASK_TYPE", w, f"invalid task type {t.kind!r}")
            if t.kind == "PERIODIC" and (t.rate_ms is None or t.rate_ms <= 0):
                self.err("TASK_RATE", w, "periodic task needs rate_ms > 0")
            if t.kind == "PERIODIC" and t.rate_ms and t.watchdog_ms < t.rate_ms:
                self.warn("TASK_WD", w, "watchdog shorter than period; verify intent")
            if not (1 <= t.priority <= 15):
                self.err("TASK_PRIO", w, "priority must be 1..15")
            for n in t.programs:
                if n.lower() not in prog_names:
                    self.err("TASK_PROG", w, f"scheduled program {n!r} does not exist")
                if n.lower() in seen_prog:
                    self.err("PROG_MULTI_TASK", w, f"program {n!r} scheduled in more than one task")
                seen_prog.add(n.lower())


    # ------------------------------------------------------------ alarms
    def _tag_type(self, tag: str, program: str) -> str | None:
        pool = list(self.p.tags)
        if program:
            pr = self.p.find_program(program)
            if pr:
                pool = pr.tags + pool
        t = next((x for x in pool if x.name.lower() == tag.lower()), None)
        return (t.data_type or "BOOL") if t else None

    def _member_type(self, data_type: str, member_path: str) -> str | None:
        """Resolve '.A.B' through UDTs; returns the leaf type, None if a member does not exist, '' if unresolvable."""
        cur = data_type
        for part in [m for m in member_path.split(".") if m]:
            part = part.split("[")[0]
            udt = next((d for d in self.p.data_types if d.name == cur), None)
            if udt is None:
                return "" if cur not in ATOMIC_TYPES else None
            m = next((x for x in udt.members if x.name.lower() == part.lower()), None)
            if m is None:
                return None
            cur = m.data_type
        return cur

    def check_alarms(self):
        if not self.p.alarms:
            return
        c = self.p.controller
        pt = c.processor_type.upper()
        supported = c.major_rev >= 31 and pt.startswith(("1756-L8", "5069-", "EMULATE 5580", "ECHO", "1756-L8"))
        if not supported:
            self.err("TAGALARM_UNSUPPORTED", "alarms", "tag-based alarms need firmware v31+ on ControlLogix 5580 / CompactLogix 5380/5480 (use ALMD instructions instead)")
        seen = set()
        for a in self.p.alarms:
            w = f"alarm {a.name}"
            self.check_name(a.name, w, "alarm")
            if a.name.lower() in seen:
                self.err("DUP_ALARM", w, "duplicate alarm name")
            seen.add(a.name.lower())
            if a.condition not in ALARM_CONDITIONS:
                self.err("ALARM_COND", w, f"condition must be one of {sorted(ALARM_CONDITIONS)}")
            if not (1 <= a.severity <= 1000):
                self.err("ALARM_SEV", w, "severity must be 1..1000")
            if not a.message:
                self.warn("ALARM_MSG", w, "alarm has no message text")
            if a.on_delay_ms % 500 or a.off_delay_ms % 500:
                self.warn("ALARM_DELAY", w, "on/off delays are evaluated every 500 ms; use multiples of 500")
            dt = self._tag_type(a.tag, a.program)
            if dt is None:
                self.err("ALARM_TAG", w, f"input tag {a.tag!r} not found in {'program ' + a.program if a.program else 'controller scope'}")
                continue
            leaf = self._member_type(dt, a.member)
            if leaf is None:
                self.err("ALARM_MEMBER", w, f"member {a.member!r} does not exist in {dt}")
            elif leaf == "BOOL" and a.condition != "TRIP":
                self.err("ALARM_COND", w, "BOOL inputs use condition TRIP")
            elif leaf and leaf != "BOOL" and a.condition == "TRIP":
                self.err("ALARM_COND", w, f"TRIP is for BOOL inputs; {leaf} needs HI/HIHI/LO/LOLO/ROC/DEV")
            if a.program:
                self.info("ALARM_SCOPE", w, "program-scope alarm input; controller scope is easier for HMI browsing")

    # ------------------------------------------------------------ hmi
    def check_hmi(self):
        try:
            from .hmi.spec import load_hmi_spec, hmi_findings
        except ImportError:
            return
        spec = load_hmi_spec(self.p)
        if spec is None:
            return
        for level, code, where, msg in hmi_findings(self.p, spec):
            self.f.append(Finding(level, code, where, msg))


    # ------------------------------------------------------------ docs
    SPEC_PLACEHOLDER = "(Describe the machine/process"

    def check_docs(self):
        """Documentation hygiene for spec directories (skipped for bare L5X input)."""
        from pathlib import Path
        root = Path(self.p.source_dir) if self.p.source_dir else None
        if not root or not root.is_dir() or not (root / "controller.json").exists():
            return
        docs = root / "docs"
        spec = docs / "SPEC.md"
        if not spec.exists():
            self.warn("DOC_SPEC", "docs/SPEC.md", "no functional specification; run plc-project-setup milestone 0")
        elif self.SPEC_PLACEHOLDER in spec.read_text(encoding="utf-8", errors="replace"):
            self.warn("DOC_SPEC", "docs/SPEC.md", "specification still contains the init placeholder")
        inputs = sorted(p for p in (docs / "input").glob("*") if p.is_file()) if (docs / "input").is_dir() else []
        if inputs:
            from .docs.extract import read_index
            indexed = {r["File"] for r in read_index(root)}
            for p in inputs:
                rel = f"input/{p.name}"
                if rel not in indexed:
                    self.warn("DOC_INPUT_UNINDEXED", f"docs/{rel}", "given document not listed in docs/INDEX.md; run `lf docs ingest`")
                elif not (docs / "extracted" / (p.stem + ".md")).exists():
                    self.info("DOC_NOT_EXTRACTED", f"docs/{rel}", "no docs/extracted text for this document; agents cannot read it cheaply")
        from .docs.generate import is_stale
        stale = is_stale(root)
        if stale:
            self.warn("DOC_STALE", "docs/generated", "generated documents are older than the spec; run `lf docs build`")
        elif stale is None:
            self.info("DOC_NONE", "docs/generated", "no generated documents yet; run `lf docs build`")


def validate(proj: Project, naming: dict | None = None) -> list[Finding]:
    return Validator(proj, naming).run()


def has_errors(findings: list[Finding]) -> bool:
    return any(f.level == "error" for f in findings)
