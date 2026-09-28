# ALS-U templates

Copied into a new project by `lf init --profile alsu`. Add approved building blocks here:

- `datatypes/*.json` site UDTs (device interfaces, alarm structures, recipe/config blocks)
- `aois/<AOI_Name>/aoi.json` + `routines/Logic.rll` site AOIs
- `hmi/faceplates/<UDT>.json` faceplate row contracts; `hmi/hmi.fragment.json` standard screens
- `docs/SPEC.template.md` the site's functional specification template

Everything here must build clean (`lf validate`) on its own; a test guards that.
