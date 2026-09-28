# ConveyorDemo - HMI tag interface

Controller-scope tags the HMI binds to. Program-scope tags are intentionally not listed.

## HMI_Conveyor01 : UDT_Motor

HMI interface for conveyor 01

| Member | Type | Direction | Description |
|---|---|---|---|
| HMI_Conveyor01.Cmd_Start | BOOL | HMI writes | HMI start command (momentary, cleared by PLC) |
| HMI_Conveyor01.Cmd_Stop | BOOL | HMI writes | HMI stop command (momentary, cleared by PLC) |
| HMI_Conveyor01.Cmd_Reset | BOOL | HMI writes | HMI fault reset (momentary, cleared by PLC) |
| HMI_Conveyor01.Sts_Run | BOOL | HMI reads | Motor is commanded to run |
| HMI_Conveyor01.Sts_Fault | BOOL | HMI reads | Motor fault latched (feedback missing) |
| HMI_Conveyor01.Sts_Ready | BOOL | HMI reads | Motor is ready to start (no fault, safety OK) |
| HMI_Conveyor01.Cfg_FaultDelay_ms | DINT | HMI writes | Feedback fault delay in milliseconds |
| HMI_Conveyor01.Sts_RunHours | REAL | HMI reads | Accumulated run hours |

## Alarms : UDT_Alarms

Line alarm bits (tag-based alarm conditions attached)

| Member | Type | Direction | Description |
|---|---|---|---|
| Alarms.Conveyor01_Fault | BOOL | read | Conveyor 01 run feedback missing |
| Alarms.EStopActive | BOOL | read | Emergency stop circuit open |
| Alarms.SimModeActive | BOOL | read | Simulation mode is active |
| Alarms.Spare | DINT | read | Spare for future alarm bits |

## Atomic tags

| Tag | Type | Access | Description |
|---|---|---|---|
| Sys_HeartBeat | BOOL | Read/Write | 1 Hz heartbeat for HMI watchdog |
| Sys_FirstScan | BOOL | Read/Write | True for the first scan after power-up/download |
| Sys_AlarmAck | BOOL | Read/Write | Global alarm acknowledge from HMI |
| Sim_Mode | BOOL | Read/Write | Simulation mode: feedback simulated, physical outputs blocked |
| I_PB_Start | BOOL | Read/Write | Local start pushbutton (NO). TODO: alias_for Local:2:I.Data.0 once I/O module XML is added |
| I_PB_Stop | BOOL | Read/Write | Local stop pushbutton (NC, 1 = healthy). TODO: alias_for Local:2:I.Data.1 |
| I_ESTOP_OK | BOOL | Read/Write | E-stop circuit healthy from safety relay. TODO: alias_for Local:2:I.Data.2 |
| I_Conveyor01_Aux | BOOL | Read/Write | Conveyor 01 contactor auxiliary contact. TODO: alias_for Local:2:I.Data.3 |
| O_Conveyor01_Run | BOOL | Read/Write | Conveyor 01 contactor coil. TODO: alias_for Local:3:O.Data.0 |

## Alarms

Tag-based alarm conditions defined in the controller (shown by PanelView 5000 Alarm Summary).

| Alarm | Input | Condition | Severity | Class | Message |
|---|---|---|---|---|---|
| Conveyor01_Fault | Alarms.Conveyor01_Fault | TRIP | 750 | Conveyor | Conveyor 01: run feedback missing (check contactor and aux contact) |
| ESTOP_Active | Alarms.EStopActive | TRIP | 1000 | Safety | Emergency stop active - clear the cause and reset the safety relay |
| SimMode_Active | Alarms.SimModeActive | TRIP | 300 | System | Simulation mode is ON - physical outputs are blocked |
