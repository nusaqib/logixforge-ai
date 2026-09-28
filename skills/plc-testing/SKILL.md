---
name: plc-testing
description: Milestone 11 - test Studio 5000 code - test plans from the spec, simulation routine (R_Sim) and Sim_ tags, Studio 5000 Logix Emulate setup, automated tests with pycomm3 against Emulate or a test controller, FAT/SAT checklists. Use when asked to test, simulate, or prove PLC logic.
---

# Testing

## Levels
1. **Static**: `lf validate` + `plc-review`. Always.
2. **Emulate**: Studio 5000 Logix Emulate (`Emulate 5570/5580` processor type, or open the L5X and
   change controller type). No physical I/O: modules are dropped; use base tags for I/O (the demo does).
3. **Test controller / bench**: real controller, I/O simulated via `R_Sim` and `Sim_Mode`.
4. **FAT/SAT**: with the machine, step through the test plan with the customer.

## Simulation support in the program
- `Sim_Mode` (controller tag) enables `R_Sim` (called last in `MainRoutine`), which writes input
  program tags from output commands with realistic delays:
  ```
  // Conveyor aux feedback follows run command after 300 ms
  XIC(Sim_Mode)XIC(Conveyor01.Run)TON(T_SimAux,?,?);
  XIC(Sim_Mode)XIC(T_SimAux.DN)OTE(I_Conveyor01_Aux);
  ```
  In real hardware `Sim_Mode` must be 0; alarm when it is 1 (`Alm_SimModeActive`).
- `R_Outputs` blocks physical outputs when `Sim_Mode` is on.

## Test plan `tests/TESTPLAN.md`
Derive one test per spec behaviour: Preconditions | Stimulus | Expected | Tag to observe | Result.
Cover: normal sequence, each interlock, each alarm (raise, ack, reset), timeouts, power-up state,
mode transitions, E-stop during each step.

## Automated tests with pycomm3 (Emulate or bench)
`tests/test_live_conveyor.py` skeleton:
```python
import time, pytest
from pycomm3 import LogixDriver
PATH = "127.0.0.1/1"        # Emulate slot, or bench controller

@pytest.fixture(scope="module")
def plc():
    with LogixDriver(PATH) as p:
        p.write(("Sim_Mode", True)); yield p; p.write(("Sim_Mode", False))

def test_start_stop(plc):
    plc.write(("I_ESTOP_OK", True), ("I_PB_Stop", True), ("HMI_Conveyor01.Cmd_Start", True))
    time.sleep(0.5)
    assert plc.read("HMI_Conveyor01.Sts_Run").value is True
    plc.write(("HMI_Conveyor01.Cmd_Stop", True)); time.sleep(0.3)
    assert plc.read("HMI_Conveyor01.Sts_Run").value is False

def test_feedback_fault(plc):
    plc.write(("Sim_Mode", False), ("HMI_Conveyor01.Cmd_Start", True))   # no simulated aux
    time.sleep(2.5)
    assert plc.read("HMI_Conveyor01.Sts_Fault").value is True
```
Run with `pytest tests/test_live_*.py`. Writes go through the guard: set `LOGIXFORGE_ALLOW_ONLINE_WRITE=1`
only for Emulate/bench, never for production.

## Evidence
Store results in `tests/results/<date>.md` with controller serial/firmware, L5X hash, tester, pass/fail.
