# Naming conventions (default house standard)

Override per project in `naming.json` (regex per kind). Logix limits: 40 chars, `[A-Za-z_][A-Za-z0-9_]*`,
no consecutive or trailing underscores, case-insensitive uniqueness, no instruction mnemonics or ST keywords.

| Kind | Pattern | Examples |
|---|---|---|
| Controller | `<Site>_<Line>_PLC` | `LineA_PLC` |
| Task | `MainTask`, `T_<Purpose>_<rate>` | `T_PID_100ms`, `SafetyTask` |
| Program | `P_<Area>` | `P_Conveyor`, `P_Utilities`, `P_Alarms` |
| Routine | `MainRoutine`, `R_<Function>` | `R_Inputs`, `R_Seq_Fill`, `R_Outputs`, `R_Sim` |
| UDT | `UDT_<Noun>` | `UDT_Motor`, `UDT_Recipe` |
| AOI | `AOI_<Noun>` | `AOI_Motor`, `AOI_AnalogIn` |
| AOI instance tag | `<Device><NN>` | `Conveyor01`, `Pump02` |
| Physical input/output alias | `I_`, `O_`, `AI_`, `AO_` + signal | `I_PB_Start`, `O_Conveyor01_Run`, `AI_TankLevel` |
| HMI interface (controller scope) | `HMI_<Device>` | `HMI_Conveyor01` |
| UDT members | `Cmd_`, `Cfg_`, `Sts_`, `Alm_`, `Sim_`, `Int_` prefixes | `Cmd_Start`, `Cfg_FaultDelay_ms`, `Sts_Run` |
| Timers / counters | `T_`, `C_` | `T_Fault`, `C_Parts` |
| One-shot storage | `ONS_<Trigger>` | `ONS_Start` |
| Alarms | `Alm_<Device>_<Condition>` | `Alm_Conveyor01_Fault` |
| Produced / consumed | `PC_<Content>` | `PC_LineStatus` |
| Simulation | `Sim_` | `Sim_Mode`, `Sim_Aux` |
| Constants | `Cfg_` + `constant: true` | `Cfg_LineSpeed_mps` |
| Units suffix | `_ms _s _min _h _degC _bar _pct _mm _rpm _mps` | `Cfg_Timeout_ms` |
| Step tags | `Step`, `Step_Last`, values 0 idle, 10..890 steps, 900+ abort/fault | |

Descriptions: sentence case, no trailing period, include units and NO/NC for I/O, include drawing
reference for physical I/O (`Start PB NO, E-101 sheet 4`).
