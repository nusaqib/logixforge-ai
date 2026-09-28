"""Logix Designer SDK adapter.

Rockwell ships the SDK as a Python wheel with Studio 5000 (v34+), typically at
  C:\\Users\\Public\\Documents\\Studio 5000\\Logix Designer SDK\\python\\
Install:  pip install "<that dir>/dist/logix_designer_sdk-*.whl"

API surface used here (async):  logix_designer_sdk.logix_project.LogixProject
  open_logix_project(path)                  save() / save_as()
  set_communications_path(path)            go_online() / go_offline()
  download(mode) / upload()                build_controller()? (varies by version)
  partial_import_from_xml_file(l5x, import_target, collision_option)
  partial_import_rungs_from_xml_file(l5x, program, routine, position, collision_option)
  get_tag_value_<TYPE>(tag_path, OperationMode) / set_tag_value_<TYPE>(...)
  change_controller_mode(ControllerMode)

Method names differ slightly across SDK releases - every call goes through `_call`, which
looks up the first matching name and raises a clear error otherwise. Run `lf sdk open --acd X`
first: it prints the methods available in the installed SDK.
"""
from __future__ import annotations

import asyncio
import json
import sys

from .pycomm3_client import require_write_permission

_CHANGING_OPS = {"import", "import-rungs", "download", "write", "mode"}


def _sdk():
    try:
        import logix_designer_sdk  # type: ignore
        from logix_designer_sdk.logix_project import LogixProject  # type: ignore
        return logix_designer_sdk, LogixProject
    except ImportError as e:
        raise SystemExit(
            "Logix Designer SDK not installed. Install the wheel shipped with Studio 5000 "
            "(Logix Designer SDK/python/dist/*.whl). See skills/plc-live-sdk/SKILL.md") from e


def _call(obj, names: list[str], *args, **kw):
    for n in names:
        fn = getattr(obj, n, None)
        if fn:
            r = fn(*args, **kw)
            return asyncio.get_event_loop().run_until_complete(r) if asyncio.iscoroutine(r) else r
    raise AttributeError(f"SDK object has none of {names}; available: {[m for m in dir(obj) if not m.startswith('_')]}")


async def _open(LogixProject, acd: str):
    return await LogixProject.open_logix_project(acd)


def cli(a):
    if a.op in _CHANGING_OPS:
        require_write_permission()
    sdk, LogixProject = _sdk()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    if not a.acd:
        sys.exit("--acd is required")
    proj = loop.run_until_complete(_open(LogixProject, a.acd))
    try:
        if a.op == "open":
            print(json.dumps({"acd": a.acd, "methods": sorted(m for m in dir(proj) if not m.startswith("_"))}, indent=2))
        elif a.op == "import":
            if not (a.l5x and a.target):
                sys.exit("--l5x and --target required (e.g. --target Controller/Programs/MainProgram)")
            coll = getattr(sdk, "ImportCollisionOptions", None)
            opt = getattr(coll, a.collision.upper(), a.collision) if coll else a.collision
            _call(proj, ["partial_import_from_xml_file", "partial_import"], a.l5x, a.target, opt)
            _call(proj, ["save"])
            print(f"imported {a.l5x} into {a.target} and saved")
        elif a.op == "import-rungs":
            if not (a.l5x and a.program and a.routine):
                sys.exit("--l5x --program --routine required")
            coll = getattr(sdk, "ImportCollisionOptions", None)
            opt = getattr(coll, a.collision.upper(), a.collision) if coll else a.collision
            _call(proj, ["partial_import_rungs_from_xml_file"], a.l5x, a.program, a.routine, -1, opt)
            _call(proj, ["save"])
            print("rungs imported and saved")
        elif a.op == "build":
            _call(proj, ["build_controller", "build", "verify_controller"])
            print("build/verify complete")
        elif a.op == "download":
            if not a.path:
                sys.exit("--path (comm path) required")
            _call(proj, ["set_communications_path"], a.path)
            mode = getattr(getattr(sdk, "ControllerMode", None), (a.mode or "Program").upper(), None)
            _call(proj, ["download"], mode) if mode is not None else _call(proj, ["download"])
            print("download complete")
        elif a.op == "upload-export":
            if not (a.path and a.output):
                sys.exit("--path and -o required")
            _call(proj, ["set_communications_path"], a.path)
            _call(proj, ["upload"])
            _call(proj, ["save_as"], a.output)
            print(f"uploaded and saved to {a.output} (export to L5X from Studio or use decompile on an .L5X save)")
        elif a.op == "online":
            _call(proj, ["set_communications_path"], a.path)
            _call(proj, ["go_online"])
            print("online")
        elif a.op in {"read", "write"}:
            if not a.tag:
                sys.exit("--tag required")
            om = getattr(sdk, "OperationMode", None)
            mode = getattr(om, "ONLINE", None) if om else None
            if a.op == "read":
                v = _call(proj, [f"get_tag_value_{a.dtype}", f"get_tag_value_{a.dtype.lower()}"], a.tag, mode)
                print(json.dumps({"tag": a.tag, "value": v}))
            else:
                caster = {"BOOL": lambda s: s.lower() in {"1", "true"}, "REAL": float, "LREAL": float, "STRING": str}.get(a.dtype, int)
                _call(proj, [f"set_tag_value_{a.dtype}", f"set_tag_value_{a.dtype.lower()}"], a.tag, mode, caster(a.value))
                print(json.dumps({"tag": a.tag, "written": a.value}))
        elif a.op == "mode":
            cm = getattr(sdk, "ControllerMode", None)
            _call(proj, ["change_controller_mode"], getattr(cm, a.mode.upper()) if cm else a.mode)
            print(f"controller mode -> {a.mode}")
    finally:
        loop.run_until_complete(proj.close()) if hasattr(proj, "close") else None
