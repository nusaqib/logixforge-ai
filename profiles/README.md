# Site profiles

A profile layers a site's or customer's standards on top of the generic LogixForge skills without
changing them. One directory per profile:

```
profiles/<name>/
  README.md            what the profile covers, source documents, version/date
  standards/*.md       the guideline, split by topic (naming, coding, hmi, alarms, safety, ...)
  naming.json          regex per kind; `lf init --profile <name>` copies it into new projects
  templates/           approved building blocks copied into new projects:
    datatypes/*.json   site UDTs
    aois/<AOI>/        site AOIs
    hmi/               hmi.json fragments and faceplate contracts
  examples/<project>/  reference projects as LogixForge specs (decompiled from real L5X / View Designer exports)
```

Pair each profile with two thin skills, `skills/<name>-plc/SKILL.md` and `skills/<name>-hmi/SKILL.md`,
that load the generic milestone skills first and then apply the profile's rules. Site agents are
optional and only worth adding once the skills are stable (see the discussion of agents vs skills in
the README).

Profiles: `alsu/` (ALS-U controls, LBNL).
