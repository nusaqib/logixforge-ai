# ConveyorDemo - Functional Specification

## Equipment
One conveyor driven by a single-direction motor via contactor with auxiliary feedback contact.

## I/O
| Tag | Type | Description |
|---|---|---|
| I_PB_Start | DI | Local start pushbutton, NO |
| I_PB_Stop | DI | Local stop pushbutton, NC (1 = healthy) |
| I_ESTOP_OK | DI | Safety relay output, 1 = circuit healthy |
| I_Conveyor01_Aux | DI | Contactor auxiliary contact |
| O_Conveyor01_Run | DO | Contactor coil |

## Behaviour
1. Start from local PB or HMI when E-stop healthy and no fault.
2. Stop from local PB, HMI, or E-stop. Stop has priority.
3. If running and no auxiliary feedback for `Cfg_FaultDelay_ms` (default 2000 ms) latch a fault, drop the output.
4. Fault reset from HMI or global alarm acknowledge, only if the cause has cleared.
5. Heartbeat 1 Hz for HMI watchdog. Accumulate run hours.

## HMI interface
`HMI_Conveyor01 : UDT_Motor` (controller scope) is the only tag the HMI writes/reads for this motor.
