---
name: plc-live-sdk
description: Milestone 12 - drive Studio 5000 through the Rockwell Logix Designer SDK (build an .ACD from a LogixForge L5X, export ACD to L5X, open .ACD, partial import, verify, download, read/write tags, change mode) and read/monitor controllers over EtherNet/IP with pycomm3. Includes the mandatory safety gate for any write. Use when the user wants an .ACD produced from a build, or to connect to, read from, upload from, or change a running controller.
---

# Live controller work and Studio 5000 automation

Two tools, one rule: **reads and file-to-file conversions are free, writes to a controller need a human.**
The plugin's PreToolUse hook blocks `lf sdk download|import|import-rungs|write|mode` and `lf online write`
until the operator sets `LOGIXFORGE_ALLOW_ONLINE_WRITE=1` in the session. Before asking for that, present:
what changes, which tags/routines, effect on running equipment, rollback plan (previous ACD/L5X saved),
and confirm the machine state (stopped / test).

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

## B. Logix Designer SDK (Windows, Studio 5000 installed, service `LdSdkService` running)
The SDK is a Windows service (server) plus a client library. `logixforge/online/ld_sdk.py` picks a client:

| Client | Comes from | Needs | Can do |
|---|---|---|---|
| `py` (preferred) | Rockwell python wheel, SDK **2.02+** (`...\Logix Designer SDK\python\...\logix_designer_sdk-*.whl`, `pip install <wheel>`) | SDK 2.x from Rockwell PCDC (Professional licence or toolkit) | open ACD/L5K/**L5X**, save-as (ACD/L5K/L5X), partial import/export, build (Logix v37+), convert revision, download, upload, tags, mode |
| `net` | the `.nupkg` Rockwell installs with Studio 5000 (`...\Logix Designer SDK\dotnet\`), SDK **1.01+**, driven through pythonnet | `pip install pythonnet`, .NET 6+ runtime, `lf sdk setup` once | SDK 1.01 (Studio v36 bundle): open ACD, save, upload, download, tags, mode. SDK 2.x nupkg: same as `py` |

Always start with `lf sdk info`: it prints the service state, the client found, its version and a capability
map (`l5x_to_acd: true/false`). Method names differ between SDK releases; the adapter tries the variants and
lists what the installed client has when none matches (`lf sdk open --acd X.ACD` prints all methods).
```
python -m logixforge.cli sdk info                                   # service, client, capabilities
python -m logixforge.cli sdk setup                                  # .NET client: unpack nupkg + NuGet deps into ~/.logixforge/ldsdk
python -m logixforge.cli sdk l5x-to-acd --l5x build/Line.L5X -o build/Line_build.ACD [--build] [--rev 36] [--overwrite]
python -m logixforge.cli sdk export     --acd Line.ACD -o Line.L5X [--detailed]        # ACD -> L5X for lf decompile/diff
python -m logixforge.cli sdk convert    --acd Old.ACD --rev 37 -o Old_v37.ACD
python -m logixforge.cli sdk open       --acd Line.ACD                                 # list client methods
python -m logixforge.cli sdk import     --acd Line.ACD --l5x build/partial/Routine_P_Conveyor_R_Conveyor.L5X --target Controller/Programs/P_Conveyor --collision Overwrite
python -m logixforge.cli sdk import-rungs --acd Line.ACD --l5x rungs.L5X --program P_Conveyor --routine R_Conveyor
python -m logixforge.cli sdk build      --acd Line.ACD                                 # verify/compile (Logix v37+, SDK 2.01+)
python -m logixforge.cli sdk download   --acd Line.ACD --path "AB_ETHIP-1\192.168.1.10\Backplane\0"
python -m logixforge.cli sdk read       --acd Line.ACD --tag Program:P_Conveyor.Step --type DINT [--path ...]   # offline value unless --path
python -m logixforge.cli sdk write      --acd Line.ACD --tag HMI_Conveyor01.Cfg_FaultDelay_ms --type DINT --value 3000
python -m logixforge.cli sdk mode       --acd Line.ACD --path ... --mode Run
python -m logixforge.cli sdk upload-export --acd Line.ACD --path ... -o Uploaded.ACD
```
- Comm path is the FactoryTalk Linx path (`AB_ETHIP-1\<ip>\Backplane\<slot>`, `EmulateEthernet\127.0.0.1`).
- Tag paths: plain `Tag` and `Program:P.Tag` are converted to the SDK XPath; an XPath passes through.
- Opening a project takes about a minute (the service loads Logix Designer components).
- File-to-file operations (`l5x-to-acd`, `export`, `convert`, `upload-export`) refuse to overwrite an
  existing file unless `--overwrite` is given: never write over the engineering master `.ACD`.
- `download` does not change the mode; the controller must already be in Program mode (`lf sdk mode`).
- The service does a FactoryTalk login for the current user; if `OpenLogixProjectAsync` fails in
  `GetTokenForCurrentUser`, open Studio 5000 once (refreshes the FactoryTalk token) and retry.
- If the Python interpreter is the Microsoft Store build, keep the .NET client outside `%LOCALAPPDATA%`
  (the default `~/.logixforge/ldsdk` is fine): the Store sandbox virtualises AppData and FtspAdapter.exe
  then fails with "Failed to resolve full path of the current executable".

### Build-to-ACD step for a project
After `lf build <project>`, produce the Studio 5000 project file next to (never over) the engineering master:
`lf sdk l5x-to-acd --l5x <project>/build/<CPU>.L5X -o <programs dir>/<CPU>_build.ACD --overwrite` (the `_build`
file is regenerated on every build, so overwriting it is intended). With SDK 1.01 the command stops with
"needs Logix Designer SDK 2.01 or later"; then import the L5X in Studio 5000 (File > Open) and save as .ACD by hand.
Whatever Studio or `--build` reports on the first import (BIT vs BOOL members, FBD_TIMER usage, timer operands) goes
into the project's SPEC.md open questions and, when it is a LogixForge defect, into `docs/BACKLOG.md`.

## Standard live-change procedure
1. **Snapshot**: upload or export the current project to L5X (`lf sdk export`); `lf decompile` it into `baseline/`.
2. **Diff intent**: make the change in the spec; `lf validate`; `lf build --partials`; `lf diff baseline/ <project>`.
3. **Review**: run `plc-review` on the diff; present the rung-level change list.
4. **Human gate**: operator confirms machine state and sets `LOGIXFORGE_ALLOW_ONLINE_WRITE=1`.
5. **Apply**: `sdk import` the partial (offline into the ACD) -> `sdk build` -> `sdk mode Program` -> `sdk download`,
   or online edit via Studio (SDK import while online creates pending edits that must be accepted/tested/assembled in Studio 5000).
6. **Verify**: `online read` the affected tags; run the test steps from `plc-testing`.
7. **Record**: save the post-change L5X, update the spec repo, note the change in `docs/CHANGELOG.md`.
8. Unset the env var.

## Do not
- Download to a controller in Run mode with equipment enabled.
- Change safety tasks online (invalidates signature).
- Leave forces enabled; check `online info` and Studio's force indicator.
- Overwrite the engineering master `.ACD` with a generated one; generated files carry a `_build` suffix.
