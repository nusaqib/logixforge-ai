"""Logix Designer SDK adapter: behaviour that must hold without Rockwell's SDK installed.

The real clients are replaced by fakes (a python-style module in sys.modules and a .NET-style class);
the live run against Studio 5000 is a manual step documented in skills/plc-live-sdk.
"""
import argparse
import io
import json
import os
import sys
import types
import zipfile
from pathlib import Path

import pytest

from logixforge.online import ld_sdk


# ----------------------------------------------------------------------------- fakes

class FakeLogixProject:
    """Python-client-like LogixProject: static openers return an instance; instance methods are async snake_case.
    Mirrors the real client, where capability checks look at the LogixProject class itself."""
    calls: list = []

    def __init__(self, path):
        self.path = path
        self.closed = False

    @classmethod
    async def open_logix_project(cls, path, *handlers):
        cls.calls.append(("open", path))
        return cls(path)

    @classmethod
    async def convert(cls, path, major):
        cls.calls.append(("convert", path, major))
        return cls(path)

    async def save_as(self, out, overwrite=False, detailed_l5x=False):
        FakeLogixProject.calls.append(("save_as", out, overwrite, detailed_l5x))
        Path(out).write_bytes(b"ACD" + Path(self.path).read_bytes()[:16])

    async def build_project(self):
        FakeLogixProject.calls.append(("build_project",))

    async def save(self):
        FakeLogixProject.calls.append(("save",))

    async def close(self):
        self.closed = True


FakeProject = FakeLogixProject   # alias used by the assertions below


class OldLogixProject2(FakeLogixProject):
    """SDK 1.x shape: opens ACD only, no save_as / convert / build."""
    save_as = None
    convert = None
    build_project = None


@pytest.fixture
def py_sdk(monkeypatch):
    def install(LogixProject):
        mod = types.ModuleType("logix_designer_sdk")
        mod.__version__ = "2.2.0-fake"
        sub = types.ModuleType("logix_designer_sdk.logix_project")
        sub.LogixProject = LogixProject
        mod.logix_project = sub
        monkeypatch.setitem(sys.modules, "logix_designer_sdk", mod)
        monkeypatch.setitem(sys.modules, "logix_designer_sdk.logix_project", sub)
        monkeypatch.setenv("LOGIXFORGE_LDSDK_BACKEND", "py")
        FakeProject.calls = []
        return ld_sdk.backend()
    return install


def _ns(**kw):
    base = dict(op=None, acd=None, l5x=None, path=None, target=None, collision="Overwrite", program=None, routine=None, tag=None,
                value=None, dtype="DINT", mode=None, output=None, overwrite=False, build=False, detailed=False, rev=None,
                sdk_dir=None, backend=None)
    base.update(kw)
    return argparse.Namespace(**base)


# ----------------------------------------------------------------------------- pure helpers

def test_net_names_and_tag_paths():
    assert ld_sdk.net_names("save_as") == ["SaveAsAsync", "SaveAs"]
    assert ld_sdk.net_names("partial_import_from_xml_file")[0] == "PartialImportFromXmlFileAsync"
    assert ld_sdk.tag_path("HPA_Sts_bi") == "Controller/Tags/Tag[@Name='HPA_Sts_bi']"
    assert ld_sdk.tag_path("Program:P100_Pit.Seq") == "Controller/Programs/Program[@Name='P100_Pit']/Tags/Tag[@Name='Seq']"
    xp = "Controller/Tags/Tag[@Name='X']"
    assert ld_sdk.tag_path(xp) == xp


def test_nuspec_deps_prefers_net6_group():
    spec = """<package><metadata><dependencies>
      <group targetFramework="net6.0">
        <dependency id="Google.Protobuf" version="3.24.3" exclude="Build,Analyzers" />
        <dependency id="Grpc.Net.Client" version="[2.57.0, )" />
      </group>
      <group targetFramework="netstandard2.0"><dependency id="Old.Thing" version="1.0.0" /></group>
    </dependencies></metadata></package>"""
    assert ld_sdk.nuspec_deps(spec) == [("Google.Protobuf", "3.24.3"), ("Grpc.Net.Client", "2.57.0")]


def test_setup_net_assembles_folder(tmp_path):
    """nupkg libs + FtspAdapter + dependency closure land in one folder, with version.txt; network injected."""
    root = tmp_path / "sdk"; (root / "dotnet").mkdir(parents=True)
    nuspec = ('<package><metadata><id>RockwellAutomation.LogixDesigner.CSClient</id><version>1.1.599</version><dependencies>'
              '<group targetFramework="net6.0"><dependency id="Dep.A" version="1.0.0" /><dependency id="System.Memory" version="4.5.0" /></group>'
              '</dependencies></metadata></package>')
    with zipfile.ZipFile(root / "dotnet" / "RockwellAutomation.LogixDesigner.CSClient.1.1.599.nupkg", "w") as z:
        z.writestr("RockwellAutomation.LogixDesigner.CSClient.nuspec", nuspec)
        z.writestr(f"lib/net6.0/{ld_sdk.NET_CLIENT_DLL}", b"MZ")
        z.writestr("FtspAdapter/FtspAdapter.exe", b"MZ")
    fetched = []

    def fetch(url):
        fetched.append(url)
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("Dep.A.nuspec", '<package><metadata><id>Dep.A</id><version>1.0.0</version><dependencies>'
                                        '<group targetFramework="net6.0"><dependency id="Dep.B" version="2.0.0" /></group></dependencies></metadata></package>'
                       if "dep.a" in url else '<package><metadata><id>Dep.B</id><version>2.0.0</version></metadata></package>')
            z.writestr("lib/netstandard2.0/" + ("Dep.A.dll" if "dep.a" in url else "Dep.B.dll"), b"MZ")
        return buf.getvalue()

    dest = tmp_path / "cache"
    rep = ld_sdk.setup_net(sdk_root=root, dest=dest, fetch=fetch)
    assert rep["version"] == "1.1.599" and rep["tfm"] == "net6.0"
    assert (dest / ld_sdk.NET_CLIENT_DLL).exists() and (dest / "FtspAdapter.exe").exists() and (dest / "version.txt").read_text() == "1.1.599"
    assert (dest / "Dep.A.dll").exists() and (dest / "Dep.B.dll").exists()
    assert len(fetched) == 2 and not any("system.memory" in u for u in fetched)   # in-box assemblies are not downloaded


def test_setup_net_without_sdk_is_a_clear_error(tmp_path):
    with pytest.raises(SystemExit, match="nupkg"):
        ld_sdk.setup_net(sdk_root=tmp_path / "nowhere", dest=tmp_path / "c", fetch=lambda u: b"")


# ----------------------------------------------------------------------------- l5x-to-acd

def test_l5x_to_acd_writes_acd_and_closes(py_sdk, tmp_path, capsys):
    be = py_sdk(FakeLogixProject)
    l5x = tmp_path / "HVPS.L5X"; l5x.write_text("<RSLogix5000Content/>")
    out = tmp_path / "out" / "HVPS_build.ACD"
    ld_sdk.cli(_ns(op="l5x-to-acd", l5x=str(l5x), output=str(out)))
    rep = json.loads(capsys.readouterr().out)
    assert out.exists() and rep["acd"] == str(out) and rep["bytes"] > 0 and rep["backend"] == "py"
    assert ("open", str(l5x)) in FakeProject.calls and ("save_as", str(out), False, False) in FakeProject.calls
    assert "build" not in rep


def test_l5x_to_acd_refuses_to_overwrite_unless_asked(py_sdk, tmp_path):
    py_sdk(FakeLogixProject)
    l5x = tmp_path / "a.L5X"; l5x.write_text("x")
    out = tmp_path / "a.ACD"; out.write_bytes(b"engineering master")
    with pytest.raises(SystemExit, match="--overwrite"):
        ld_sdk.cli(_ns(op="l5x-to-acd", l5x=str(l5x), output=str(out)))
    assert out.read_bytes() == b"engineering master"
    ld_sdk.cli(_ns(op="l5x-to-acd", l5x=str(l5x), output=str(out), overwrite=True))
    assert out.read_bytes().startswith(b"ACD") and ("save_as", str(out), True, False) in FakeProject.calls


def test_l5x_to_acd_build_and_convert(py_sdk, tmp_path, capsys):
    py_sdk(FakeLogixProject)
    l5x = tmp_path / "a.L5X"; l5x.write_text("x")
    ld_sdk.cli(_ns(op="l5x-to-acd", l5x=str(l5x), output=str(tmp_path / "b.ACD"), build=True, rev=37))
    rep = json.loads(capsys.readouterr().out)
    assert rep["build"] == "ok" and ("convert", str(l5x), 37) in FakeProject.calls and ("build_project",) in FakeProject.calls


def test_l5x_to_acd_missing_source(py_sdk, tmp_path):
    py_sdk(FakeLogixProject)
    with pytest.raises(SystemExit, match="not found"):
        ld_sdk.cli(_ns(op="l5x-to-acd", l5x=str(tmp_path / "missing.L5X"), output=str(tmp_path / "x.ACD")))


def test_sdk1_client_reports_needs_sdk2(py_sdk, tmp_path):
    """SDK 1.01 (Studio 5000 v36 bundle) has no save-as: the command must say so instead of failing inside the SDK."""
    py_sdk(OldLogixProject2)
    l5x = tmp_path / "a.L5X"; l5x.write_text("x")
    with pytest.raises(SystemExit, match="SDK 2.01"):
        ld_sdk.cli(_ns(op="l5x-to-acd", l5x=str(l5x), output=str(tmp_path / "b.ACD")))
    assert not (tmp_path / "b.ACD").exists()


def test_export_acd_to_l5x(py_sdk, tmp_path, capsys):
    py_sdk(FakeLogixProject)
    acd = tmp_path / "a.ACD"; acd.write_bytes(b"acd")
    out = tmp_path / "a.L5X"
    ld_sdk.cli(_ns(op="export", acd=str(acd), output=str(out), detailed=True))
    assert out.exists() and ("save_as", str(out), False, True) in FakeProject.calls


def test_info_reports_capabilities(py_sdk, capsys):
    py_sdk(FakeLogixProject)
    ld_sdk.cli(_ns(op="info"))
    d = json.loads(capsys.readouterr().out)
    assert d["client"] == "py" and d["l5x_to_acd"] is True and d["capabilities"]["build_project"] is True
    assert d["capabilities"]["partial_import_from_xml_file"] is False and "service" in d


def test_info_without_any_client(monkeypatch, capsys, tmp_path):
    monkeypatch.setitem(sys.modules, "logix_designer_sdk", None)   # import raises ImportError
    monkeypatch.setenv("LOGIXFORGE_LDSDK_DIR", str(tmp_path / "empty"))
    monkeypatch.setattr(ld_sdk, "NET_CACHE", tmp_path / "empty")
    monkeypatch.delenv("LOGIXFORGE_LDSDK_BACKEND", raising=False)
    ld_sdk.cli(_ns(op="info"))
    d = json.loads(capsys.readouterr().out)
    assert d["client"] is None and "lf sdk setup" in d["error"]


def test_changing_ops_still_gated(py_sdk, tmp_path, monkeypatch):
    py_sdk(FakeLogixProject)
    monkeypatch.delenv("LOGIXFORGE_ALLOW_ONLINE_WRITE", raising=False)
    from logixforge.online.pycomm3_client import OnlineWriteBlocked
    for op in ["download", "import", "write", "mode"]:
        with pytest.raises(OnlineWriteBlocked):
            ld_sdk.cli(_ns(op=op, acd="x.ACD"))
    assert ld_sdk._FILE_OPS.isdisjoint(ld_sdk._CHANGING_OPS)
