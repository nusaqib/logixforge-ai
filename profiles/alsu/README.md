# ALS-U controls profile

Site profile for ALS-U (Advanced Light Source Upgrade, LBNL) PLC and HMI work with Studio 5000
Logix Designer and Studio 5000 View Designer.

## Status
Scaffold. To be filled from:
- [ ] ALS-U controls guideline document(s) -> `standards/` (split by topic, keep the source version/date here)
- [ ] `naming.json` derived from the guideline's naming rules
- [ ] Reference project: L5X export -> `examples/<project>/` via `lf decompile`
- [ ] Reference HMI: View Designer project export -> `examples/<project>/hmi-export/` and `hmi/hmi.json`
- [ ] Approved UDTs/AOIs -> `templates/`

## Sources
| Document | Version | Date | Notes |
|---|---|---|---|
| (add) | | | |

## Layout
```
standards/   naming.md, coding.md, hmi.md, alarms.md, safety.md, io.md   (one topic per file)
naming.json  regex per kind used by `lf validate`
templates/   datatypes/, aois/, hmi/
examples/    reference projects as specs
```

## Usage
```
lf init projects/<Name> --name <Ctrl> --profile alsu       # copies naming.json and templates
```
Then load the `alsu-plc` / `alsu-hmi` skills; they load the generic skills and apply these standards.
