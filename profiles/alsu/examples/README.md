# ALS-U reference projects

Each subfolder is a real ALS-U project as a LogixForge spec, used by the skills as the worked example
and by the reviewer as the style reference.

To add one:
```
# PLC: Studio 5000 > File > Save As > .L5X
lf decompile <export.L5X> -o profiles/alsu/examples/<project>
# HMI: View Designer > File > Export Project, copy the folder to
#      profiles/alsu/examples/<project>/hmi-export/   (raw .hmi files, reference for syntax and layout)
lf validate profiles/alsu/examples/<project>
```
Remove or anonymise anything that must not be in the repository (IP addresses, credentials, drawings).
