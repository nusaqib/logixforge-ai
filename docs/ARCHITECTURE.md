# Architecture

## Layers
1. **Spec** (text, LLM-friendly, diffable): JSON for structure (controller, UDTs, AOIs, tags, tasks),
   `.rll` (neutral rung text) and `.st` for logic, verbatim XML for I/O modules.
2. **Model** (`logixforge/model.py`): dataclasses mirroring Logix concepts.
3. **Loader** (`project.py`) and **reader** (`l5x/reader.py`) both produce the model, so
   validation, inspection and diff work on specs and on Studio 5000 exports alike.
4. **Validator** (`validate.py`): Logix hard rules (errors) + house standards (warnings/info).
   Rung text is parsed by `rll.py` into an instruction tree; ST gets lightweight structural checks.
5. **Writer** (`l5x/writer.py`): model -> L5X, full controller or partial import documents.
6. **Interfaces**: CLI (`cli.py`), MCP server (`mcp_server.py`), Claude Code plugin (skills, agents,
   commands, hooks).
7. **Documentation** (`docs/`): `extract.py` (given PDF/DOCX/XLSX/CSV/images -> `docs/extracted/*.md`, `docs/INDEX.md`, spec hash),
   `generate.py` (model -> `docs/generated/` Markdown/CSV with Mermaid; cause-and-effect derived from the rung tree and ST
   assignments), `export.py` (pandoc wrapper). Docs are one-directional: inputs feed the spec, outputs are derived from it.
8. **Online**: `online/pycomm3_client.py` (CIP read/write) and `online/ld_sdk.py` (Logix Designer SDK
   adapter). Both gated by `require_write_permission()`.

## Why neutral rung text instead of XML per instruction
Studio 5000 itself stores ladder as rung text inside L5X. It is compact, exactly what engineers
copy/paste in the editor, and models produce it reliably. The parser gives us structure for validation
without inventing a new language.

## Why milestone skills
Each milestone has different rules, files and failure modes. Small, focused skills keep the model's
context relevant and let teams override one milestone (e.g. a customer naming standard) without
touching the rest.

## Extending
- New instruction: add to `rll.INSTRUCTIONS` with operand counts.
- New validation: add a method on `Validator`, a code in `standards/review-checklist.md`, a test.
- New routine type (FBD/SFC): extend `Routine`, loader, writer, reader; FBD sheets are XML and are
  passed through verbatim today.
- HMI: `logixforge/hmi/reader.py` reads a View Designer export (screens, folders, navigation, shortcuts, bindings, AOG use,
  security) for documentation and review; `logixforge/docs/hmi_nav.py` builds one navigation model from either that or hmi.json.
- HMI: `logixforge/hmi/spec.py` (hmi.json + faceplate derivation + validation) and
  `logixforge/hmi/viewdesigner.py` (text .hmi emitter). A FactoryTalk/Optix emitter would consume the same `HmiSpec`.
