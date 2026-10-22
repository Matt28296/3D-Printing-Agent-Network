"""import_fcstd against the reference FreeCAD assembly in docs/reference/excavator."""
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

pytest.importorskip("build123d")

ROOT = Path(__file__).resolve().parent.parent
FCSTD = ROOT / "docs" / "reference" / "excavator" / "AssemblyExample.FCStd"


@pytest.fixture(scope="module")
def ref(tmp_path_factory):
    out = tmp_path_factory.mktemp("ref")
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "import_fcstd.py"), str(FCSTD), "--out", str(out)],
                       capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, r.stderr
    return out, json.loads((out / "reference.json").read_text())


def test_parts_and_sizes(ref):
    _, r = ref
    parts = {p["label"]: p for p in r["parts"]}
    assert len(parts) == 13
    assert parts["BasePin"]["bbox_mm"] == [20.0, 20.0, 100.0]
    assert parts["BasePin"]["volume_cm3"] == pytest.approx(31.4, abs=0.1)
    assert parts["Boom"]["volume_cm3"] == pytest.approx(1204.6, abs=1)


def test_bed_fit_and_scale(ref):
    _, r = ref
    assert sorted(r["summary"]["parts_too_big_for_bed"]) == ["Boom", "Stick"]
    assert r["summary"]["max_uniform_scale_all_parts_fit"] == pytest.approx(0.617, abs=0.002)
    boom = next(p for p in r["parts"] if p["label"] == "Boom")
    assert "split" in boom["split_hint"]


def test_joints_and_diameters(ref):
    _, r = ref
    assert len(r["joints"]) == 16 and r["grounded"] == ["BasePin"]
    rev = next(j for j in r["joints"] if j["name"] == "Revolute")
    assert [s["part"] for s in rev["between"]] == ["BasePin", "Base"]
    assert [s["diameter_mm"] for s in rev["between"]] == [20.0, 20.0]
    assert "zero clearance" in rev["print_note"]
    types = {j["type"] for j in r["joints"]}
    assert types == {"Revolute", "Slider", "Cylindrical"}


def test_files_written(ref):
    out, r = ref
    for p in r["parts"]:
        for f in p["files"].values():
            assert (out / f).stat().st_size > 1000
    assert (out / "reference.md").read_text().startswith("# Reference")
    assert (out / "assembly.png").stat().st_size > 5000


def test_reference_step_builds_through_cad_build(tmp_path):
    job = ROOT / "jobs" / "_pytest_fcstd"
    shutil.rmtree(job, ignore_errors=True)
    job.mkdir(parents=True)
    try:
        (job / "model.py").write_text(
            "from build123d import Rot, import_step\nfrom cadlib import to_bed\n"
            "def build():\n    return to_bed(Rot(0, 90, 0) * import_step('../../docs/reference/excavator/parts/BasePin.step'))\n")
        r = subprocess.run([sys.executable, str(ROOT / "tools" / "cad_build.py"), str(job)],
                           capture_output=True, text=True, timeout=300)
        assert r.returncode == 0, r.stderr
        assert json.loads((job / "geometry.json").read_text())["bbox_mm"] == [100.0, 20.0, 20.0]
    finally:
        shutil.rmtree(job, ignore_errors=True)


def test_rejects_non_fcstd(tmp_path):
    bad = tmp_path / "x.FCStd"
    bad.write_text("not a zip")
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "import_fcstd.py"), str(bad)],
                       capture_output=True, text=True)
    assert r.returncode == 2
    assert zipfile.is_zipfile(FCSTD)
