"""Data model for a Logix project spec.

The spec is deliberately small and text-first so an LLM agent can author it
one milestone at a time (controller -> data types -> tags -> routines ->
programs/tasks -> AOIs -> I/O) and a deterministic writer turns it into L5X.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

ATOMIC_TYPES = {"BOOL", "SINT", "INT", "DINT", "LINT", "USINT", "UINT", "UDINT", "ULINT", "REAL", "LREAL"}
PREDEFINED_TYPES = ATOMIC_TYPES | {
    "STRING", "TIMER", "COUNTER", "CONTROL", "PID", "PIDE", "MESSAGE", "ALARM", "ALARM_DIGITAL",
    "ALARM_ANALOG", "FBD_TIMER", "FBD_COUNTER", "FBD_ONESHOT", "FBD_BOOLEAN_AND", "FBD_COMPARE",
    "FBD_CONVERT", "FBD_LIMITER", "FBD_LOGICAL", "FBD_MASK_EQUAL", "FBD_MASKED_MOVE", "FBD_MATH",
    "FBD_MATH_ADVANCED", "FBD_TRUNCATE", "AXIS_CIP_DRIVE", "AXIS_VIRTUAL", "MOTION_GROUP",
    "MOTION_INSTRUCTION", "PHASE", "PHASE_INSTRUCTION", "AUX_VALVE_CONTROL", "DISCRETE_2STATE",
    "DISCRETE_3STATE", "SEQUENCER", "TOTALIZER", "SCALE", "DEADTIME", "DERIVATIVE", "FILTER_HIGH_PASS",
    "FILTER_LOW_PASS", "FUNCTION_GENERATOR", "INTEGRATOR", "LEAD_LAG", "MAXIMUM_CAPTURE", "MINIMUM_CAPTURE",
    "MOVING_AVERAGE", "MOVING_STD_DEV", "RAMP_SOAK", "RATE_LIMITER", "SELECT", "SELECTED_SUMMER",
    "UP_DOWN_ACCUM", "HL_LIMIT", "IMC", "CC", "MMC", "DATALOG_INSTRUCTION", "S_CURVE", "FLIP_FLOP_D",
    "FLIP_FLOP_JK", "DOMINANT_RESET", "DOMINANT_SET", "SELECTABLE_NEGATE", "SPLIT_RANGE", "PROP_INT",
    "LOGIX_TIME", "HMIBC", "ANALOG_ALARM", "MODULE", "SFC_STEP", "SFC_ACTION", "SFC_STOP", "CAM", "CAM_PROFILE",
    "OUTPUT_CAM", "OUTPUT_COMPENSATION", "COORDINATE_SYSTEM", "MOTION_GROUP", "EXT_ROUTINE_CONTROL",
    "EXT_ROUTINE_PARAMETERS", "SERIAL_PORT_CONTROL", "AXIS_CONSUMED", "AXIS_GENERIC", "AXIS_GENERIC_DRIVE",
    "AXIS_SERVO", "AXIS_SERVO_DRIVE", "DATALOG_INSTRUCTION", "REDUNDANCY_INFO",
}


def is_known_type(name: str, known: set) -> bool:
    """Module-defined types look like 'AB:5069_IB16:I:0' or '_000A:SD4840E2_...:O:0'."""
    return name in known or ":" in name


@dataclass
class Member:
    name: str
    data_type: str
    dimension: int = 0
    description: str = ""
    radix: Optional[str] = None
    external_access: str = "Read/Write"


@dataclass
class DataType:
    name: str
    members: list[Member] = field(default_factory=list)
    description: str = ""
    family: str = "NoFamily"  # "StringFamily" for string UDTs


@dataclass
class Tag:
    name: str
    data_type: str = ""
    dimensions: str = ""          # "" | "10" | "4,8"
    description: str = ""
    alias_for: str = ""           # if set, TagType=Alias
    value: object = None          # L5K-format initial value (scalar, list, or dict)
    constant: bool = False
    external_access: str = "Read/Write"
    radix: Optional[str] = None
    usage: str = ""               # for program parameters: Input/Output/InOut/Public
    produced: Optional[dict] = None
    consumed: Optional[dict] = None
    scope: str = "controller"     # filled by loader


@dataclass
class Rung:
    text: str
    comment: str = ""
    number: int = 0
    rung_type: str = "N"


@dataclass
class Routine:
    name: str
    kind: str = "RLL"             # RLL | ST | FBD | SFC (writer supports RLL and ST)
    description: str = ""
    rungs: list[Rung] = field(default_factory=list)
    st_lines: list[str] = field(default_factory=list)
    fbd_sheets_xml: str = ""      # raw <FBDContent> body if authored externally


@dataclass
class Program:
    name: str
    main_routine: str = "MainRoutine"
    fault_routine: str = ""
    description: str = ""
    disabled: bool = False
    tags: list[Tag] = field(default_factory=list)
    routines: list[Routine] = field(default_factory=list)
    kind: str = "Normal"          # Normal | Safety


@dataclass
class Task:
    name: str
    kind: str = "CONTINUOUS"      # CONTINUOUS | PERIODIC | EVENT
    rate_ms: Optional[float] = None
    priority: int = 10
    watchdog_ms: int = 500
    programs: list[str] = field(default_factory=list)
    description: str = ""
    inhibit: bool = False
    disable_update_outputs: bool = False
    event_trigger: str = ""
    event_tag: str = ""


@dataclass
class AOIParameter:
    name: str
    data_type: str = "BOOL"
    usage: str = "Input"          # Input | Output | InOut
    required: bool = False
    visible: bool = True
    description: str = ""
    default: object = None
    dimension: int = 0
    external_access: str = "Read/Write"


@dataclass
class AOI:
    name: str
    revision: str = "1.0"
    description: str = ""
    vendor: str = ""
    parameters: list[AOIParameter] = field(default_factory=list)
    local_tags: list[Tag] = field(default_factory=list)
    routines: list[Routine] = field(default_factory=list)
    execute_prescan: bool = False
    execute_postscan: bool = False
    execute_enable_in_false: bool = False
    revision_note: str = ""


@dataclass
class Module:
    name: str
    catalog_number: str
    parent: str = "Local"
    parent_port_id: int = 1
    address: str = ""             # slot number or IP address
    port_type: str = "ICP"        # ICP (chassis) | Ethernet
    vendor: int = 1
    product_type: int = 0
    product_code: int = 0
    major: int = 1
    minor: int = 1
    inhibited: bool = False
    major_fault: bool = False
    ekey: str = "CompatibleModule"
    description: str = ""
    raw_xml: str = ""             # verbatim <Module> element from a Studio 5000 export (preferred)


ALARM_CONDITIONS = {"TRIP", "HIHI", "HI", "LO", "LOLO", "ROC_POS", "ROC_NEG", "DEV_HI", "DEV_LO"}


@dataclass
class Alarm:
    """Tag-based alarm condition (Logix v31+, 5x80 controllers). Shown by PanelView 5000 / FT Alarms."""
    name: str
    tag: str                      # base tag the condition is attached to
    member: str = ""              # ".Member.Sub" relative path inside the tag ("" = the tag itself)
    message: str = ""
    severity: int = 500           # 1..1000
    condition: str = "TRIP"       # see ALARM_CONDITIONS; TRIP for BOOL inputs
    limit: float = 0.0
    on_delay_ms: int = 0
    off_delay_ms: int = 0
    deadband: float = 0.0
    latched: bool = False
    ack_required: bool = True
    alarm_class: str = ""
    hmi_group: str = ""
    program: str = ""             # set when the tag is program-scoped
    used: bool = True
    target_tag: str = ""          # DEV_HI/DEV_LO reference
    lang: str = "en-US"

    @property
    def input_path(self) -> str:
        return self.tag + self.member


@dataclass
class Controller:
    name: str
    processor_type: str = "1756-L83E"
    major_rev: int = 33
    minor_rev: int = 11
    description: str = ""
    time_slice: int = 20
    software_revision: str = "33.00"
    safety: bool = False
    chassis_size: int = 10
    slot: int = 0
    power_loss_program: str = ""     # PowerLossProgram (power-up handler)
    major_fault_program: str = ""    # MajorFaultProgram (controller fault handler)


@dataclass
class Project:
    controller: Controller
    data_types: list[DataType] = field(default_factory=list)
    modules: list[Module] = field(default_factory=list)
    aois: list[AOI] = field(default_factory=list)
    tags: list[Tag] = field(default_factory=list)
    programs: list[Program] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)
    alarms: list[Alarm] = field(default_factory=list)
    source_dir: str = ""

    # ---- lookups -------------------------------------------------------
    def data_type_names(self) -> set[str]:
        return {d.name for d in self.data_types} | {a.name for a in self.aois} | PREDEFINED_TYPES

    def find_program(self, name: str) -> Optional[Program]:
        return next((p for p in self.programs if p.name.lower() == name.lower()), None)

    def controller_tag_names(self) -> set[str]:
        return {t.name.lower() for t in self.tags}
