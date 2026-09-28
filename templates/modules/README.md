# Module XML library

Drop verified `<Module>` elements exported from Studio 5000 here, one file per catalog number and
firmware major, e.g. `1756-IB16_v33.xml`, `1756-OB16E_v33.xml`, `5069-IB16_v33.xml`, `PowerFlex525_v33.xml`.

To use one in a project: copy it to `<project>/modules/<InstanceName>.xml` and edit `Name`, `Address`
(slot or IP), `ParentModule` and `ParentModPortId`. Everything else stays as exported.

Why not generated: module profiles carry connection formats, config assemblies and product codes
that Studio 5000 validates on import; hand-written variants are rejected or silently wrong.
