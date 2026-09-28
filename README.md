# LogixForge

Agentic PLC programming for **Rockwell Studio 5000** (ControlLogix / CompactLogix / GuardLogix).
A Claude Code plugin plus a Python toolkit: frontier models write a text-first project spec,
LogixForge validates it and compiles it to **L5X** for import into Studio 5000, and (optionally)
reviews or modifies a **live controller** through pycomm3 and the Logix Designer SDK.

```
spec (JSON + .rll/.st)  --lf build-->  L5X  --import-->  Studio 5000  --download-->  controller
        ^                                                     |                          |
        +------------------ lf decompile <-- export/upload ---+---- pycomm3 / SDK -------+
```

## What is here
| Path | Purpose |
|---|---|
| `skills/` | One skill per milestone: project setup, UDTs, AOIs, tags, I/O modules, programs/tasks, ladder, structured text, alarms, safety, review, export/import, testing, live SDK, documentation (in and out, including as-built docs for existing ACD/L5X projects), HMI for Studio 5000 View Designer (FactoryTalk/Optix on the roadmap) |
| `agents/` | `plc-architect` (plan), `plc-builder` (implement), `plc-reviewer` (audit, read-only) |
| `commands/` | `/lf-new`, `/lf-build`, `/lf-validate`, `/lf-review`, `/lf-import`, `/lf-online`, `/lf-docs`, `/lf-document-existing` |
| `hooks/` | Blocks writes to live controllers without operator opt-in; auto-validates spec edits |
| `logixforge/` | Python toolkit: spec loader, rung parser, validator, L5X writer/reader, View Designer HMI generator, CLI, MCP server, online adapters |
| `standards/` | Naming, coding standard, review checklist, L5X and instruction references |
| `examples/conveyor-demo/` | Complete small project (UDT, AOI, ladder + ST, tasks, alarms, HMI) that builds and imports clean |
| `profiles/` | Site profiles (standards, naming, templates, reference projects) layered on the generic skills; `profiles/alsu/` for ALS-U |
| `tests/` | pytest suite for the toolkit |

## Install
```powershell
# toolkit (stdlib only; extras are optional)
pip install -e .                 # gives the `lf` command
pip install -e ".[dev,mcp,online]"   # + pytest, MCP server, pycomm3

# Claude Code plugin (from this folder)
claude plugin marketplace add E:\gitsrc\logixforge-ai
claude plugin install logixforge@logixforge-marketplace
# or for development:  claude --plugin-dir E:\gitsrc\logixforge-ai
```
Logix Designer SDK (for `lf sdk ...`): install the wheel shipped with Studio 5000 v34+
(`C:\Users\Public\Documents\Studio 5000\Logix Designer SDK\python\dist\`). See `skills/plc-live-sdk`.

## Quick start
```powershell
lf init projects\LineA --name LineA_PLC --processor 1756-L83E --rev 33 [--profile alsu]
# ... let the agent fill datatypes/, aois/, tags/, programs/, tasks.json (skills guide it) ...
lf validate projects\LineA
lf build projects\LineA --partials
# Studio 5000: File > Open > projects\LineA\build\LineA_PLC.L5X   (or right-click > Import for partials)
```
Try the demo: `lf build examples\conveyor-demo --partials` then open `examples\conveyor-demo\build\ConveyorDemo.L5X`.

## Projects and documentation
One git repository per PLC project (`lf init <dir> --name X --git`); this repository holds the plugin,
`examples/` and `profiles/` only. Documents you receive go in with `lf docs ingest` (kept verbatim in
`docs/input/`, read by the agent from `docs/extracted/`), their content is moved into the spec, and the
deliverable document set is generated from the spec with `lf docs build` (Markdown, Mermaid diagrams;
`lf docs export` makes PDF/DOCX through pandoc). See the `plc-documentation` skill.

## Project spec layout
```
controller.json          processor, firmware, description
datatypes/*.json         UDTs
aois/<AOI>/aoi.json      parameters, local tags;  aois/<AOI>/routines/Logic.rll
tags/*.json              controller-scope tags (aliases, HMI UDTs, produced/consumed)
modules/*.xml            <Module> elements copied from a Studio 5000 export
programs/<P>/program.json, tags.json, routines/*.rll | *.st
tasks.json               continuous / periodic / event tasks
alarms.json              tag-based alarm conditions (messages, severity, class) attached to controller tags
hmi/hmi.json             HMI screens/widgets; faceplates derive from UDTs (lf hmi build -> View Designer import folder)
naming.json              regex per kind, enforced by the validator
docs/SPEC.md             functional specification (the agent keeps it in sync)
docs/INDEX.md, input/, extracted/   given documents (PDF/DOCX/XLSX/drawings) as received + their Markdown text (lf docs ingest)
docs/generated/          SYSTEM overview, I/O list, tags, routine map, cause-and-effect, alarms, HMI tags + navigation, test plan (lf docs build; committed)
build/                   generated L5X, HMI package, exported PDF/DOCX (git-ignored)
```
Ladder is written as Studio 5000 neutral rung text, one rung per block, `//` comments above:
```
// Seal-in start/stop, stop has priority
[XIC(PB_Start),XIC(Run)]XIC(PB_Stop_OK)XIO(Fault)OTE(Run);
```

## CLI
`lf init [--git] | validate | build | partial | inspect | decompile | diff | rung check | hmi build | docs build|ingest|export | online | sdk`
(`python -m logixforge.cli ...` works without installing). `lf --help` for options.

## MCP server
`python -m logixforge.mcp_server` exposes `lf_validate`, `lf_build`, `lf_partial`, `lf_inspect`,
`lf_decompile`, `lf_check_rung`, `lf_hmi_build`, `lf_docs_build`, `lf_docs_ingest`, `lf_online_read`, `lf_online_tags`, `lf_online_write` to any MCP
client. The plugin registers it automatically via `.mcp.json`.

## HMI (Studio 5000 View Designer / PanelView 5000)
`hmi/hmi.json` describes screens as widgets bound to controller-scope tags; `lf hmi build` writes a
View Designer import folder (`ViewApplication.hmi`, `User-Defined Screens/*.hmi`, one Add-On Graphic
faceplate per UDT, navigation shortcuts) in the text format of Rockwell publication 9324-RM001 (v9+).
Alarms are defined in the controller (`alarms.json` -> Logix tag-based alarm conditions) and shown by
the PanelView's predefined Alarm Summary. Import: create a controller reference named as
`controller_ref`, then File > Import Project. Element names the manual does not document verbatim are
listed in `logixforge/hmi/viewdesigner.py:UNVERIFIED` for the first import round.

## Safety model
- Offline by default. Nothing touches a controller unless you run `lf online` / `lf sdk`.
- Any write, download, import or mode change is refused until the operator sets
  `LOGIXFORGE_ALLOW_ONLINE_WRITE=1` for the session, and the Claude Code hook blocks the agent from
  running such commands before that.
- LogixForge validates structure and references. **Studio 5000 must still verify/compile**, and
  safety functions must be validated and signed by a qualified engineer.

## Status and roadmap
- Done: spec format, validator, L5X writer (full + partial), reader/decompile/diff, CLI, MCP,
  hooks, skills, agents, demo, tests.
- Verified: the demo L5X imports into Studio 5000 v33 (1756-L83E) with **zero errors**, and
  generated files round-trip through the reader. Import findings are folded into the writer and
  the validator (see `standards/l5x-reference.md`, "Things that break import").
- New: tag-based alarms in L5X (`alarms.json`) and a View Designer HMI generator; both await their
  first import into Studio 5000 / View Designer.
- Next: FBD/SFC routine authoring, module XML library, FactoryTalk View / Optix generation,
  Logix Emulate test harness, alarm definitions on UDT/AOI definitions, CI action that builds and validates.

## Contributing
Add a pattern to a skill, a rule to `logixforge/validate.py` with a test, or a module XML to
`templates/modules/`. Keep skills short and imperative; put long reference material in `standards/`.

MIT licensed.
