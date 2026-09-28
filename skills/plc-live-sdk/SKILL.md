---
name: plc-live-sdk
description: Milestone 12 - review and modify a live/online Studio 5000 project with the Rockwell Logix Designer SDK (open .ACD, partial import L5X, verify, download, go online, read/write tags, change mode) and read/monitor controllers over EtherNet/IP with pycomm3. Includes the mandatory safety gate for any write. Use when the user wants to connect to, read from, upload from, or change a running controller.
---

# Live controller work

Two tools, one rule: **reads are free, writes need a human.** The plugin's PreToolUse hook blocks
write/download/import/mode commands until the operator sets `LOGIXFORGE_ALLOW_ONLINE_WRITE=1` in
the session. Before asking for that, present: what changes, which tags/routines, effect on running
equipment, rollback plan (previous ACD/L5X saved), and confirm the machine state (stopped / test).

## A. pycomm3 (EtherNet/IP, no Studio needed) - monitoring, review, test stimulation
```
pip install pycomm3
python -m logixforge.cli online info  --path 192.168.1.10/0          # 'ip/slot' or 'ip/bp/2'
python -m logixforge.cli online tags  --path 192.168.1.10/0 [--program P_Conveyor]
python -m logixforge.cli online read  --path 192.168.1.10/0 HMI_Conveyor01.Sts_Run Program:P_Conveyor.Step
python -m logixforge.cli online write --path 192.168.1.10/0 Program:P_Conveyor.Sim_Mode=1   # gated
```
- Program-scope tags are `Program:<Prog>.<Tag>`. Structures read as dicts.
- Use for: verifying a state machine against the spec, capturing values for a review, driving
  `Sim_` inputs in Emulate, soak tests. Cannot change logic.
- Never write to `O_`/output aliases or safety tags; write to `Cmd_`/`Sim_`/`Cfg_` tags only.

## B. Logix Designer SDK (Windows, Studio 5000 v34+, SDK licence) - change the program
Install: the SDK ships with Studio 5000 (`C:\Users\Public\Documents\Studio 5000\Logix Designer SDK\python\dist\*.whl`);
`pip install <wheel>`. The API is async; the adapter `logixforge/online/ld_sdk.py` wraps it and
prints available methods for the installed version (`lf sdk open --acd X.ACD`) because method names
vary between releases. Verify the names before relying on a workflow.
```
python -m logixforge.cli sdk open          --acd C:\proj\Line.ACD
python -m logixforge.cli sdk import        --acd Line.ACD --l5x build/partial/Routine_P_Conveyor_R_Conveyor.L5X --target Controller/Programs/P_Conveyor --collision Overwrite
python -m logixforge.cli sdk import-rungs  --acd Line.ACD --l5x rungs.L5X --program P_Conveyor --routine R_Conveyor
python -m logixforge.cli sdk build         --acd Line.ACD                       # verify/compile
python -m logixforge.cli sdk download      --acd Line.ACD --path "AB_ETHIP-1\192.168.1.10\Backplane\0" --mode Program
python -m logixforge.cli sdk online        --acd Line.ACD --path ...
python -m logixforge.cli sdk read          --acd Line.ACD --tag Program:P_Conveyor.Step --type DINT
python -m logixforge.cli sdk write         --acd Line.ACD --tag HMI_Conveyor01.Cfg_FaultDelay_ms --type DINT --value 3000
python -m logixforge.cli sdk mode          --acd Line.ACD --mode Run
python -m logixforge.cli sdk upload-export --acd Line.ACD --path ... -o Uploaded.ACD
```
Comm path format is the RSLinx/FactoryTalk Linx path (`AB_ETHIP-1\<ip>\Backplane\<slot>`).

## Standard live-change procedure
1. **Snapshot**: upload or export the current project to L5X; `lf decompile` it into `baseline/`.
2. **Diff intent**: make the change in the spec; `lf validate`; `lf build --partials`; `lf diff baseline/ <project>`.
3. **Review**: run `plc-review` on the diff; present the rung-level change list.
4. **Human gate**: operator confirms machine state and sets `LOGIXFORGE_ALLOW_ONLINE_WRITE=1`.
5. **Apply**: `sdk import` the partial (offline into the ACD) -> `sdk build` -> `sdk download` in
   Program mode, or online edit via Studio (SDK import while online creates pending edits that must be
   accepted/tested/assembled in Studio 5000).
6. **Verify**: `online read` the affected tags; run the test steps from `plc-testing`.
7. **Record**: save the post-change L5X, update the spec repo, note the change in `docs/CHANGELOG.md`.
8. Unset the env var.

## Do not
- Download to a controller in Run mode with equipment enabled.
- Change safety tasks online (invalidates signature).
- Leave forces enabled; check `online info` and Studio's force indicator.
