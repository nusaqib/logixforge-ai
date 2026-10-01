"""Logix Designer SDK adapter (Rockwell "Logix Designer SDK", server = Windows service LdSdkService).

Two client backends, chosen automatically (override with LOGIXFORGE_LDSDK_BACKEND=py|net):

  py   Rockwell's Python client `logix_designer_sdk` (SDK 2.02+; wheel in
       C:\\Users\\Public\\Documents\\Studio 5000\\Logix Designer SDK\\python\\...\\*.whl, `pip install <wheel>`).
       Opens ACD / L5K / L5X, save_as (ACD / L5K / L5X), partial import/export, build (Logix v37+),
       download, upload, tag read/write, controller mode, convert to a newer major revision.
  net  Rockwell's .NET client (nupkg in ...\\Logix Designer SDK\\dotnet\\, SDK 1.01+) driven through
       pythonnet (`pip install pythonnet`, .NET 6+ runtime). `lf sdk setup` unpacks the nupkg, copies
       FtspAdapter.exe and fetches the NuGet dependencies into ~/.logixforge/ldsdk (LOGIXFORGE_LDSDK_DIR).
       SDK 1.01 (bundled with Studio 5000 v36) opens .ACD only: save, upload, download, tags, mode.
       L5X -> ACD, save-as and partial import need SDK 2.01+ (separate download from Rockwell PCDC,
       Professional licence or toolkit).

Method names differ between releases; every call goes through `Backend.call(proj, names, ...)`
which tries snake_case (py) or PascalCase[Async] (net) variants and raises a clear error listing the
methods the installed client actually has. `lf sdk info` prints backend, version and capabilities.

Tag paths are the SDK's XPath form; `tag_path()` converts plain `Tag` and `Program:P.Tag`.

Safety: operations in `_CHANGING_OPS` need LOGIXFORGE_ALLOW_ONLINE_WRITE=1 (`require_write_permission`);
file-to-file operations (l5x-to-acd, export, convert) never touch a controller and refuse to
overwrite an existing output unless `--overwrite` is given.
"""
from __future__ import annotations

import asyncio
import glob
import io
import json
import os
import re
import subprocess
import sys
import zipfile
from pathlib import Path

from .pycomm3_client import require_write_permission

_CHANGING_OPS = {"import", "import-rungs", "download", "write", "mode"}
_FILE_OPS = {"l5x-to-acd", "export", "convert"}

SDK_ROOT = Path(os.environ.get("LOGIXFORGE_LDSDK_ROOT", r"C:\Users\Public\Documents\Studio 5000\Logix Designer SDK"))
# Not under %LOCALAPPDATA%: the Microsoft Store Python virtualises AppData, and the SDK's FtspAdapter.exe child process
# then cannot resolve its own path ("Failed to resolve full path of the current executable").
NET_CACHE = Path(os.environ.get("LOGIXFORGE_LDSDK_DIR") or Path.home() / ".logixforge" / "ldsdk")
NET_CLIENT_DLL = "RockwellAutomation.LogixDesigner.LogixProject.CSClient.dll"
# lowest runtime the shipped client needs first (net6.0 for SDK 1.x/2.x); newer TFMs only when nothing older exists
_TFM_PREF = ["net6.0", "netstandard2.1", "netstandard2.0", "net5.0", "netcoreapp3.1", "net7.0", "net8.0"]
# .NET assemblies that ship inside the shared runtime; never fetched from NuGet
_INBOX = {"system.memory", "system.buffers", "system.runtime.compilerservices.unsafe", "system.threading.tasks.extensions",
          "system.numerics.vectors", "microsoft.bcl.asyncinterfaces", "system.diagnostics.diagnosticsource", "system.text.json",
          "system.text.encodings.web", "system.valuetuple", "netstandard.library", "microsoft.netcore.platforms",
          "microsoft.netcore.targets", "microsoft.csharp"}

NEEDS_SDK2 = ("needs Logix Designer SDK 2.01 or later (the installed client has no save-as / L5X support; "
              "SDK 1.01 bundled with Studio 5000 v36 opens .ACD only). Install SDK 2.x from Rockwell PCDC "
              "(Professional licence or toolkit), then `pip install` its python wheel or run `lf sdk setup`.")


# --------------------------------------------------------------------------- helpers

def _pascal(snake: str) -> str:
    return "".join(p[:1].upper() + p[1:] for p in snake.split("_"))


def _variants(snake) -> list[str]:
    """A method may be named differently across SDK releases (`build_project` in the guide, `build` in 2.0.2)."""
    names = [snake] if isinstance(snake, str) else list(snake)
    return names + [a for n in names for a in ALIASES.get(n, []) if a not in names]


ALIASES = {"build_project": ["build"], "build": ["build_project"], "close": ["dispose"]}


def net_names(snake) -> list[str]:
    """`save_as` -> ['SaveAsAsync', 'SaveAs']  (the .NET client suffixes awaitables with Async)."""
    out = []
    for n in _variants(snake):
        p = _pascal(n)
        out += [p + "Async", p]
    return out


def tag_path(name: str) -> str:
    """Plain `Tag` -> Controller/Tags/Tag[@Name='Tag']; `Program:P.Tag` -> program-scope XPath; XPath passes through."""
    if "/" in name or "[" in name:
        return name
    m = re.match(r"^Program:([A-Za-z_][\w]*)\.(.+)$", name)
    if m:
        return f"Controller/Programs/Program[@Name='{m.group(1)}']/Tags/Tag[@Name='{m.group(2)}']"
    return f"Controller/Tags/Tag[@Name='{name}']"


def _enum(container, enum_name: str, member: str):
    """Case-insensitive enum member lookup (`RequestedControllerMode.Program` vs `PROGRAM`), None if absent."""
    en = getattr(container, enum_name, None)
    if en is None:
        return None
    for m in dir(en):
        if m.lower() == member.lower():
            return getattr(en, m)
    return None


def _refuse_overwrite(out: str, overwrite: bool):
    if os.path.exists(out) and not overwrite:
        raise SystemExit(f"{out} exists; pass --overwrite to replace it (never write over the engineering master)")


def service_status() -> str:
    """State of the LdSdkService Windows service ('Running', 'Stopped', 'not installed', or 'unknown' off Windows)."""
    if os.name != "nt":
        return "unknown"
    try:
        r = subprocess.run(["sc", "query", "LdSdkService"], capture_output=True, text=True, timeout=10)
    except Exception:
        return "unknown"
    if r.returncode != 0:
        return "not installed"
    m = re.search(r"STATE\s*:\s*\d+\s+(\w+)", r.stdout)
    return m.group(1).title() if m else "unknown"


# --------------------------------------------------------------------------- backends

class Backend:
    kind = "?"
    version = "?"

    def supports(self, snake: str) -> bool: ...
    def open(self, path: str): ...
    def static(self, snake: str, *args): ...
    def call(self, proj, snake: str, *args): ...
    def close(self, proj): ...
    def methods(self, proj) -> list[str]:
        return sorted(m for m in dir(proj) if not m.startswith("_"))
    def enum(self, enum_name: str, member: str):
        return None


class PyBackend(Backend):
    """Rockwell python client (async API)."""
    kind = "py"

    def __init__(self):
        try:
            import logix_designer_sdk  # type: ignore
            from logix_designer_sdk.logix_project import LogixProject  # type: ignore
        except ImportError as e:
            raise ImportError("logix_designer_sdk not installed") from e
        self.sdk, self.LogixProject = logix_designer_sdk, LogixProject
        self.version = getattr(logix_designer_sdk, "__version__", None) or "?"
        if self.version == "?":
            try:
                from importlib.metadata import version
                self.version = version("logix_designer_sdk")
            except Exception:
                pass
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def _run(self, r):
        return self.loop.run_until_complete(r) if asyncio.iscoroutine(r) else r

    def _find(self, obj, snake):
        return next((getattr(obj, n) for n in _variants(snake) if getattr(obj, n, None)), None)

    def supports(self, snake):
        return self._find(self.LogixProject, snake) is not None

    def open(self, path):
        return self._run(self.LogixProject.open_logix_project(path))

    def static(self, snake, *args):
        fn = self._find(self.LogixProject, snake)
        if fn is None:
            raise AttributeError(f"python SDK has no LogixProject.{snake}")
        return self._run(fn(*args))

    def call(self, proj, snake, *args):
        fn = self._find(proj, snake)
        if fn is None:
            raise AttributeError(f"SDK project has no method {snake}; available: {self.methods(proj)}")
        return self._run(fn(*args))

    def close(self, proj):
        fn = self._find(proj, "close")
        if fn:
            self._run(fn())

    def enum(self, enum_name, member):
        for holder in (self.sdk, getattr(self.sdk, "enums", None), self.LogixProject):
            v = _enum(holder, enum_name, member) if holder is not None else None
            if v is not None:
                return v
        try:
            import importlib
            return _enum(importlib.import_module("logix_designer_sdk.enums"), enum_name, member)
        except Exception:
            return None


class NetBackend(Backend):
    """Rockwell .NET client through pythonnet (CoreCLR)."""
    kind = "net"

    def __init__(self, bindir: Path | None = None):
        self.bindir = Path(bindir or NET_CACHE)
        dll = self.bindir / NET_CLIENT_DLL
        if not dll.exists():
            raise FileNotFoundError(f"{dll} not found; run `lf sdk setup` (unpacks the SDK nupkg from {SDK_ROOT / 'dotnet'})")
        try:
            from pythonnet import load  # type: ignore
            load("coreclr")
            import clr  # type: ignore
        except Exception as e:  # pragma: no cover - depends on the machine
            raise ImportError("pythonnet (and a .NET 6+ runtime) is required for the .NET SDK client: pip install pythonnet") from e
        sys.path.append(str(self.bindir))
        clr.AddReference(str(dll))
        import RockwellAutomation.LogixDesigner as ns  # type: ignore
        self.ns, self.LogixProject = ns, ns.LogixProject
        vt = self.bindir / "version.txt"
        self.version = vt.read_text().strip() if vt.exists() else "?"

    @staticmethod
    def _result(r):
        # Task / Task<T>: block on it like `await`; anything else is already a value
        aw = getattr(r, "GetAwaiter", None)
        return aw().GetResult() if aw else r

    def _find(self, obj, snake):
        return next((getattr(obj, n) for n in net_names(snake) if getattr(obj, n, None) is not None), None)

    def supports(self, snake):
        return self._find(self.LogixProject, snake) is not None

    def open(self, path):
        return self._result(self.LogixProject.OpenLogixProjectAsync(path))

    def static(self, snake, *args):
        fn = self._find(self.LogixProject, snake)
        if fn is None:
            raise AttributeError(f".NET SDK has no LogixProject.{net_names(snake)}")
        return self._result(fn(*args))

    def call(self, proj, snake, *args):
        fn = self._find(proj, snake)
        if fn is None:
            raise AttributeError(f"SDK project has none of {net_names(snake)}; available: {self.methods(proj)}")
        return self._result(fn(*args))

    def close(self, proj):
        if hasattr(proj, "Dispose"):
            proj.Dispose()

    def enum(self, enum_name, member):
        return _enum(self.LogixProject, enum_name, member) or _enum(self.ns, enum_name, member)


def backend(prefer: str | None = None) -> Backend:
    prefer = prefer or os.environ.get("LOGIXFORGE_LDSDK_BACKEND")
    errors = []
    for kind in ([prefer] if prefer else ["py", "net"]):
        try:
            return PyBackend() if kind == "py" else NetBackend()
        except (ImportError, FileNotFoundError) as e:
            errors.append(f"{kind}: {e}")
    raise SystemExit("No Logix Designer SDK client available.\n  " + "\n  ".join(errors) +
                     "\nInstall Rockwell's python wheel (SDK 2.02+) or run `lf sdk setup` for the .NET client "
                     "(needs `pip install pythonnet`). See skills/plc-live-sdk/SKILL.md")


# --------------------------------------------------------------------------- .NET client setup

def nuspec_deps(nuspec_xml: str) -> list[tuple[str, str]]:
    """(id, version) pairs of the best matching dependency group of a .nuspec (net8 > net6 > netstandard)."""
    groups = re.findall(r'<group targetFramework="([^"]+)">(.*?)</group>', nuspec_xml, re.S)
    body = None
    for want in ["net8.0", ".NETCoreApp8.0", "net7.0", "net6.0", ".NETCoreApp6.0", "net5.0", "netstandard2.1", ".NETStandard2.1",
                 "netstandard2.0", ".NETStandard2.0"]:
        body = next((b for tf, b in groups if tf.lower() == want.lower()), None)
        if body is not None:
            break
    if body is None:
        body = groups[0][1] if groups else nuspec_xml
    return [(d, v) for d, v in re.findall(r'<dependency id="([^"]+)" version="\[?([0-9][\w.\-]*)', body)]


def _extract_libs(z: zipfile.ZipFile, dest: Path) -> str | None:
    libs = [n for n in z.namelist() if n.startswith("lib/") and n.lower().endswith((".dll", ".xml"))]
    tfms = {n.split("/")[1] for n in libs}
    pick = next((t for t in _TFM_PREF if t in tfms), None)
    if pick:
        for n in libs:
            if n.split("/")[1] == pick:
                (dest / os.path.basename(n)).write_bytes(z.read(n))
    return pick


def setup_net(sdk_root: Path = SDK_ROOT, dest: Path = NET_CACHE, fetch=None) -> dict:
    """Assemble a runnable folder for the .NET client: SDK nupkg libs + FtspAdapter.exe + NuGet dependency closure.

    `fetch(url) -> bytes` is injectable for tests; default uses urllib against api.nuget.org.
    """
    pkgs = sorted(glob.glob(str(sdk_root / "dotnet" / "RockwellAutomation.LogixDesigner.CSClient.*.nupkg")))
    if not pkgs:
        raise SystemExit(f"no RockwellAutomation.LogixDesigner.CSClient.*.nupkg under {sdk_root / 'dotnet'}; is the Logix Designer SDK installed?")
    pkg = pkgs[-1]
    dest.mkdir(parents=True, exist_ok=True)
    if fetch is None:
        import urllib.request

        def fetch(url):  # pragma: no cover - network
            return urllib.request.urlopen(url).read()
    report = {"nupkg": pkg, "dest": str(dest), "packages": []}
    with zipfile.ZipFile(pkg) as z:
        nuspec = next(n for n in z.namelist() if n.endswith(".nuspec"))
        spec = z.read(nuspec).decode("utf-8", "ignore")
        version = re.search(r"<version>([^<]+)</version>", spec).group(1)
        (dest / "version.txt").write_text(version)
        report["version"] = version
        report["tfm"] = _extract_libs(z, dest)
        for n in z.namelist():
            if n.lower().endswith("ftspadapter.exe"):
                (dest / "FtspAdapter.exe").write_bytes(z.read(n))
        todo = nuspec_deps(spec)
    done = set()
    while todo:
        pid, ver = todo.pop()
        key = pid.lower()
        if key in done or key in _INBOX or key.startswith("system.") or key.startswith("runtime."):
            continue
        done.add(key)
        data = fetch(f"https://api.nuget.org/v3-flatcontainer/{key}/{ver.lower()}/{key}.{ver.lower()}.nupkg")
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            spec = z.read(next(n for n in z.namelist() if n.endswith(".nuspec"))).decode("utf-8", "ignore")
            tfm = _extract_libs(z, dest)
            report["packages"].append({"id": pid, "version": ver, "tfm": tfm})
            todo.extend(nuspec_deps(spec))
    return report


# --------------------------------------------------------------------------- operations

def l5x_to_acd(be: Backend, l5x: str, out: str, overwrite=False, build=False, rev: int | None = None) -> dict:
    """Open an L5X (or L5K/ACD) as a project and save it as .ACD; optionally convert the major revision and build/verify."""
    if not os.path.exists(l5x):
        raise SystemExit(f"{l5x} not found")
    if not be.supports("save_as"):
        raise SystemExit(f"l5x-to-acd {NEEDS_SDK2}")
    _refuse_overwrite(out, overwrite)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    proj = be.static("convert", l5x, int(rev)) if rev else be.open(l5x)
    result = {"source": l5x, "acd": out, "backend": be.kind, "sdk": be.version}
    try:
        if build:
            if be.supports("build_project"):
                be.call(proj, "build_project")
                result["build"] = "ok"
            else:
                result["build"] = "not available in this SDK (build needs Logix Designer v37+ / SDK 2.01+)"
        be.call(proj, "save_as", out, bool(overwrite))
    finally:
        be.close(proj)
    if not os.path.exists(out) or os.path.getsize(out) == 0:
        raise SystemExit(f"save_as reported success but {out} is missing or empty")
    result["bytes"] = os.path.getsize(out)
    return result


def export_project(be: Backend, acd: str, out: str, overwrite=False, detailed=False) -> dict:
    """ACD -> L5X/L5K (the SDK's save-as with a different extension); `detailed` adds references/context/IO tags."""
    if not be.supports("save_as"):
        raise SystemExit(f"export {NEEDS_SDK2}")
    _refuse_overwrite(out, overwrite)
    proj = be.open(acd)
    try:
        be.call(proj, "save_as", out, bool(overwrite), bool(detailed))
    finally:
        be.close(proj)
    return {"acd": acd, "out": out, "bytes": os.path.getsize(out), "backend": be.kind}


def info(be: Backend | None) -> dict:
    caps = ["open_acd", "save", "download", "upload", "upload_to_new_project", "get_tag_value", "set_tag_value", "change_controller_mode"]
    d = {"service": service_status(), "sdk_root": str(SDK_ROOT), "sdk_root_present": SDK_ROOT.exists()}
    if be is None:
        d["client"] = None
        return d
    d.update(client=be.kind, version=be.version)
    d["capabilities"] = {c: True for c in caps}
    for c in ["save_as", "partial_import_from_xml_file", "partial_export_to_xml_file", "build_project", "convert", "upload_to_new_project"]:
        d["capabilities"][c] = be.supports(c)
    d["l5x_to_acd"] = d["capabilities"]["save_as"]
    return d


# --------------------------------------------------------------------------- CLI

def cli(a):
    if a.op in _CHANGING_OPS:
        require_write_permission()
    if a.op == "setup":
        print(json.dumps(setup_net(dest=Path(a.sdk_dir) if getattr(a, "sdk_dir", None) else NET_CACHE), indent=2))
        return
    if a.op == "info":
        try:
            be = backend(getattr(a, "backend", None))
        except SystemExit as e:
            d = info(None); d["error"] = str(e)
            print(json.dumps(d, indent=2)); return
        print(json.dumps(info(be), indent=2)); return

    be = backend(getattr(a, "backend", None))
    if a.op == "l5x-to-acd":
        if not (a.l5x and a.output):
            sys.exit("--l5x <built.L5X> -o <new.ACD> required")
        print(json.dumps(l5x_to_acd(be, a.l5x, a.output, overwrite=a.overwrite, build=a.build, rev=a.rev), indent=2)); return
    if a.op == "export":
        if not (a.acd and a.output):
            sys.exit("--acd <project.ACD> -o <export.L5X> required")
        print(json.dumps(export_project(be, a.acd, a.output, overwrite=a.overwrite, detailed=a.detailed), indent=2)); return
    if a.op == "convert":
        if not (a.acd and a.output and a.rev):
            sys.exit("--acd <project> --rev <major revision> -o <converted.ACD> required")
        print(json.dumps(l5x_to_acd(be, a.acd, a.output, overwrite=a.overwrite, rev=a.rev), indent=2)); return

    if not a.acd:
        sys.exit("--acd is required")
    proj = be.open(a.acd)
    try:
        if a.op == "open":
            print(json.dumps({"acd": a.acd, "client": be.kind, "sdk": be.version, "methods": be.methods(proj)}, indent=2))
        elif a.op == "import":
            if not (a.l5x and a.target):
                sys.exit("--l5x and --target required (e.g. --target Controller/Programs/MainProgram)")
            opt = be.enum("ImportCollisionOptions", a.collision) or a.collision
            # SDK 2.0.2 signature: (x_path, xml_file_to_import, collision_option, continue_on_errors=False)
            be.call(proj, "partial_import_from_xml_file", a.target, a.l5x, opt)
            be.call(proj, "save")
            print(f"imported {a.l5x} into {a.target} and saved")
        elif a.op == "import-rungs":
            if not (a.l5x and a.program and a.routine):
                sys.exit("--l5x --program --routine required")
            opt = be.enum("ImportCollisionOptions", a.collision) or a.collision
            be.call(proj, "partial_import_rungs_from_xml_file", a.l5x, a.program, a.routine, -1, opt)
            be.call(proj, "save")
            print("rungs imported and saved")
        elif a.op == "build":
            if not be.supports("build_project"):
                sys.exit("build/verify is not available in this SDK (needs Logix Designer v37+ and SDK 2.01+); open the ACD in Studio 5000 and Verify")
            be.call(proj, "build_project")
            if a.output:
                _refuse_overwrite(a.output, a.overwrite)
                be.call(proj, "save_as", a.output, bool(a.overwrite))
            else:
                be.call(proj, "save")
            print("build/verify complete")
        elif a.op == "download":
            if not a.path:
                sys.exit("--path (comm path) required")
            be.call(proj, "set_communications_path", a.path)
            be.call(proj, "download")
            print("download complete (controller must already be in Program mode; use `lf sdk mode` first)")
        elif a.op == "upload-export":
            if not (a.path and a.output):
                sys.exit("--path and -o required")
            _refuse_overwrite(a.output, a.overwrite)
            be.call(proj, "set_communications_path", a.path)
            be.call(proj, "upload")
            if be.supports("save_as"):
                be.call(proj, "save_as", a.output, bool(a.overwrite))
            else:
                be.call(proj, "save")
                print(f"SDK 1.x: upload merged into {a.acd} and saved there (no save-as); -o ignored", file=sys.stderr)
            print(f"uploaded; {a.output if be.supports('save_as') else a.acd} written")
        elif a.op == "online":
            be.call(proj, "set_communications_path", a.path)
            be.call(proj, "go_online")
            print("online")
        elif a.op in {"read", "write"}:
            if not a.tag:
                sys.exit("--tag required")
            mode = be.enum("TagOperationMode", "Online" if a.path else "Offline") or be.enum("OperationMode", "Online" if a.path else "Offline")
            if a.path:
                be.call(proj, "set_communications_path", a.path)
            path = tag_path(a.tag)
            if a.op == "read":
                v = be.call(proj, f"get_tag_value_{a.dtype.lower()}", path, mode)
                print(json.dumps({"tag": a.tag, "path": path, "value": v}, default=str))
            else:
                caster = {"BOOL": lambda s: s.lower() in {"1", "true"}, "REAL": float, "LREAL": float, "STRING": str}.get(a.dtype, int)
                be.call(proj, f"set_tag_value_{a.dtype.lower()}", path, mode, caster(a.value))
                be.call(proj, "save")
                print(json.dumps({"tag": a.tag, "path": path, "written": a.value}))
        elif a.op == "mode":
            if a.path:
                be.call(proj, "set_communications_path", a.path)
            be.call(proj, "change_controller_mode", be.enum("RequestedControllerMode", a.mode) or be.enum("ControllerMode", a.mode) or a.mode)
            print(f"controller mode -> {a.mode}")
    finally:
        be.close(proj)
