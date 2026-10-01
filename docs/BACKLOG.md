# LogixForge production-grade backlog

Defects and gaps found while using LogixForge on real projects. Each item is closed by a fix plus a regression test. Source project in brackets.

| # | Item | Found | Status |
|---|---|---|---|
| 1 | Decompile wrote every unnamed I/O module to `modules/.xml` (18 of 20 modules lost on round trip) | HVPS 2026-10-01 | fixed: `module_file_stem()` keys unnamed modules by parent, slot, catalog |
| 2 | Multi-line routine description emitted as one `//!` line; continuation lines parsed as rung text (`RUNG_SYNTAX`) | HVPS 2026-10-01 | fixed: one `//!` per line on write, loader consumes all leading `//!` lines |
| 3 | `ROUTINE_UNCALLED` false positive for routines called with `JSR()` from structured text | HVPS 2026-10-01 | fixed: ST JSR detection, with `JSR_TARGET` check |
| 4 | `guard_online` hook blocked inline Python containing `file.write("...")` | HVPS 2026-10-01 | fixed: pattern requires a driver-like receiver |
| 5 | SYSTEM.md architecture Mermaid uses node id `m_` for every unnamed module (duplicate ids, broken diagram) | HVPS 2026-10-01 | fixed: ids and labels from parent and slot (`_mname`) |
| 6 | Controller `Local` module (Ethernet port config, IP) is dropped on decompile and not re-emitted on build; round trip loses the controller IP when set | HVPS 2026-10-01 | open: capture port addresses in `controller.json` and emit them |
| 7 | `lf docs ingest` of an `.L5X` reports "NOT EXTRACTED: unsupported format" in INDEX.md although indexing as provenance is the intent | HVPS 2026-10-01 | fixed: `.l5x`/`.acd` are provenance rows (`PROVENANCE_EXT`), test in `test_docs.py` |
| 8 | UDT BOOL members are read as `BIT` from exports and written back as `BOOL`; confirm Studio 5000 import accepts it or emit `BIT` with hidden host members | HVPS 2026-10-01 | verified 2026-10-01 with SDK 2.02: a round-trip build (BOOL members, no hidden host SINTs) opens in Studio 5000 v36 with 0 errors, 2 warnings; no writer change needed |
| 9 | Validator does not report the 500-byte EPICS array limit or unnamed modules as findings | HVPS 2026-10-01 | open |
| 10 | No end-to-end test with a real multi-chassis export (unnamed modules, ST JSR, multi-line descriptions) | HVPS 2026-10-01 | fixed: `tests/test_roundtrip_regressions.py` |
| 11 | `serialize()` restored CDATA per line, so any multi-line description or comment produced malformed XML (hidden until item 2 preserved full descriptions) | HVPS 2026-10-01 | fixed: whole-text CDATA restoration |
| 12 | ST line-comment stripping in the validator used DOTALL, so one `//` comment swallowed the rest of the routine | HVPS 2026-10-01 | fixed |
| 13 | `lf sdk` assumed Rockwell's python wheel; the SDK bundled with Studio 5000 v36 is 1.01 (.NET/C++ only), so no `lf sdk` command worked on a standard v36 machine | HVPS 2026-10-01 | fixed: two client backends (`py` wheel, `net` nupkg via pythonnet), `lf sdk setup` assembles the .NET client, `lf sdk info` reports capabilities; default client folder outside `%LOCALAPPDATA%` (Store Python virtualisation broke FtspAdapter.exe) |
| 14 | No build-to-ACD step: `lf build` ends at an L5X that a human imports in Studio 5000 | HVPS 2026-10-01 | fixed in code: `lf sdk l5x-to-acd` (open L5X, optional convert/build, save-as .ACD, overwrite refused by default) + `export`/`convert`; needs SDK 2.01+ at run time (open L5X / save-as absent in 1.01); live run 2026-10-01 with SDK 2.02 / python client 2.0.2: original export and round-trip build → ACD in ~45 s |
| 15 | SDK tag paths: `lf sdk read/write` passed bare tag names, the SDK wants XPath (`Controller/Tags/Tag[@Name='X']`) | HVPS 2026-10-01 | fixed: `tag_path()` converts `Tag` and `Program:P.Tag` |

