# I/O modules

Module definitions carry connection formats, config data and product codes that only Studio 5000
knows exactly. Do not hand-write them. Instead:

1. In Studio 5000 add the module once (or open any project that has it).
2. Right-click the module > **Export Module...** (or export the whole project to L5X).
3. Copy the complete `<Module ...>...</Module>` element into `modules/<Name>.xml`.

LogixForge inlines each `.xml` verbatim into the built L5X and the I/O tags
(`Local:2:I`, `Local:2:O`, ...) become valid alias targets.

The demo project has no modules so it builds and downloads to Logix Emulate as-is; the `I_*` / `O_*`
tags are plain BOOLs you can toggle by hand.
