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
| 7 | `lf docs ingest` of an `.L5X` reports "NOT EXTRACTED: unsupported format" in INDEX.md although indexing as provenance is the intent | HVPS 2026-10-01 | open: treat `.l5x` as provenance kind, no extraction message |
| 8 | UDT BOOL members are read as `BIT` from exports and written back as `BOOL`; confirm Studio 5000 import accepts it or emit `BIT` with hidden host members | HVPS 2026-10-01 | open: verify on first import, add writer test |
| 9 | Validator does not report the 500-byte EPICS array limit or unnamed modules as findings | HVPS 2026-10-01 | open |
| 10 | No end-to-end test with a real multi-chassis export (unnamed modules, ST JSR, multi-line descriptions) | HVPS 2026-10-01 | fixed: `tests/test_roundtrip_regressions.py` |
| 11 | `serialize()` restored CDATA per line, so any multi-line description or comment produced malformed XML (hidden until item 2 preserved full descriptions) | HVPS 2026-10-01 | fixed: whole-text CDATA restoration |
| 12 | ST line-comment stripping in the validator used DOTALL, so one `//` comment swallowed the rest of the routine | HVPS 2026-10-01 | fixed |
