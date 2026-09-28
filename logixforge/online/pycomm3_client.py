"""Thin pycomm3 wrapper.  pip install logixforge[online]"""
from __future__ import annotations

import os


class OnlineWriteBlocked(PermissionError):
    pass


def require_write_permission():
    """Writes to a live controller are blocked unless the operator opts in for this session.

    Set LOGIXFORGE_ALLOW_ONLINE_WRITE=1 (the Claude Code hook in hooks/guard_online.py also
    enforces a human confirmation before any write/download command is run).
    """
    if os.environ.get("LOGIXFORGE_ALLOW_ONLINE_WRITE") != "1":
        raise OnlineWriteBlocked(
            "Writing to a live controller is disabled. Set LOGIXFORGE_ALLOW_ONLINE_WRITE=1 after a human "
            "has reviewed the change and confirmed the machine is in a safe state.")


def _plc(path: str):
    try:
        from pycomm3 import LogixDriver
    except ImportError as e:
        raise SystemExit("pycomm3 not installed: pip install pycomm3") from e
    return LogixDriver(path)


def controller_info(path: str) -> dict:
    with _plc(path) as plc:
        info = dict(plc.info)
        info.pop("tasks", None)
        return info


def list_tags(path: str, program: str | None = None) -> list[dict]:
    with _plc(path) as plc:
        out = []
        for name, t in plc.tags.items():
            if program and not name.startswith(f"Program:{program}."):
                continue
            if not program and name.startswith("Program:"):
                continue
            out.append({"name": name, "type": t.get("data_type_name") or t.get("data_type"), "dim": t.get("dimensions"),
                        "alias": t.get("alias")})
        return out


def read_tags(path: str, tags: list[str]) -> list[dict]:
    with _plc(path) as plc:
        res = plc.read(*tags)
        if not isinstance(res, list):
            res = [res]
        return [{"tag": r.tag, "value": r.value, "type": r.type, "error": r.error} for r in res]


def write_tags(path: str, values: dict[str, str]) -> list[dict]:
    require_write_permission()
    with _plc(path) as plc:
        pairs = []
        for k, v in values.items():
            t = plc.get_tag_info(k.split(".")[0].split("[")[0]) or {}
            dt = (t.get("data_type_name") or t.get("data_type") or "").upper()
            if dt == "BOOL" or k.endswith("]") and "." in k:
                v = v.lower() in {"1", "true", "on"}
            elif dt in {"REAL", "LREAL"}:
                v = float(v)
            elif dt in {"SINT", "INT", "DINT", "LINT", "USINT", "UINT", "UDINT", "ULINT"}:
                v = int(v)
            pairs.append((k, v))
        res = plc.write(*pairs)
        if not isinstance(res, list):
            res = [res]
        return [{"tag": r.tag, "value": r.value, "error": r.error} for r in res]
