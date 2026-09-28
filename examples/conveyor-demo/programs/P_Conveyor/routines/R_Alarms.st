//! Alarm evaluation (Structured Text). Alarm bits live in the controller tag 'Alarms'; tag-based alarm conditions (alarms.json) give them messages for the HMI.
// Individual alarm bits
Alarms.Conveyor01_Fault := Conveyor01.Fault;
Alarms.EStopActive := NOT ESTOP_OK;
Alarms.SimModeActive := Sim_Mode;

// Summary for HMI banner
Alarm_Any := Alarms.Conveyor01_Fault OR Alarms.EStopActive;

// Global acknowledge resets the motor fault (only acts when the cause has cleared)
IF Sys_AlarmAck THEN
    HMI_Conveyor01.Cmd_Reset := 1;
    Sys_AlarmAck := 0;
END_IF;
