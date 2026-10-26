"""cadlib, cad_build, render and mesh_check. Skipped when build123d/trimesh aren't installed."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip("build123d")
pytest.importorskip("trimesh")

ROOT = Path(__file__).resolve().parent.parent
COOKBOOK = ROOT / "docs" / "cad-cookbook"


def run(tool, *args):
    return subprocess.run([sys.executable, str(ROOT / "tools" / tool), *map(str, args)],
                          capture_output=True, text=True, timeout=600)


@pytest.fixture
def job(tmp_path):
    j = tmp_path / "jobs" / "20261017-test"
    j.mkdir(parents=True)
    return j


def test_cadlib_helpers():
    from build123d import Box, Align
    import cadlib as c

    block = Box(30, 20, 10, align=(Align.MIN, Align.MIN, Align.MIN))
    part = block - c.teardrop_cutter(c.comp(4.0), 40, axis="X", center=(15, 10, 5))
    part = part - c.vertical_hole_cutter(3.0, 10, top_center=(5, 5, 10))
    part = part - c.hex_nut_pocket(5.5, 3, bottom_center=(24, 10, 0))
    part = c.chamfer_bottom(part, 0.4)
    holes = c.measure_holes(part)
    diam = sorted(h["diameter"] for h in holes)
    assert diam == [3.0, 4.2]
    td = next(h for h in holes if h["diameter"] == 4.2)
    assert td["axis"] == [1.0, 0.0, 0.0] and 260 <= td["arc_deg"] <= 280
    assert c.bbox(part)["size"] == [30.0, 20.0, 10.0]
    with pytest.raises(ValueError):
        c.teardrop_cutter(4, 10, axis="Z")
    lifted = c.to_bed(Box(5, 5, 5))
    assert abs(lifted.bounding_box().min.Z) < 1e-9


def test_measure_holes_sees_trimmed_teardrops():
    """A teardrop made as cylinder + rotated box leaves a trimmed cylindrical face (build123d radius None)."""
    from build123d import Align, Box, Cylinder, Pos, Rot
    import cadlib as c

    r = 1.8
    cutter = Pos(0, 0, -1) * Cylinder(r, 6, align=(Align.CENTER, Align.CENTER, Align.MIN))
    cutter += Pos(0, r / 2 ** 0.5, -1) * Rot(0, 0, 45) * Box(r, r, 6, align=(Align.CENTER, Align.CENTER, Align.MIN))
    plate = Box(20, 20, 4, align=(Align.CENTER, Align.CENTER, Align.MIN)) - cutter
    holes = c.measure_holes(plate)
    assert [h["diameter"] for h in holes] == [3.6]
    assert holes[0]["axis"] == [0.0, 0.0, 1.0] and 260 <= holes[0]["arc_deg"] <= 280


@pytest.mark.parametrize("example", sorted(p.name for p in COOKBOOK.glob("*.py")))
def test_cookbook_examples_build(job, example):
    shutil.copy(COOKBOOK / example, job / "model.py")
    r = run("cad_build.py", job)
    assert r.returncode == 0, r.stderr
    geo = json.loads((job / "geometry.json").read_text())
    assert geo["watertight"] and geo["fits_bed"] and geo["solids"] == 1 and abs(geo["min_z_mm"]) < 0.01


def test_l_bracket_geometry(job):
    shutil.copy(COOKBOOK / "l_bracket.py", job / "model.py")
    assert run("cad_build.py", job).returncode == 0
    geo = json.loads((job / "geometry.json").read_text())
    assert geo["bbox_mm"] == [40.0, 40.0, 20.0]
    assert sorted(h["diameter"] for h in geo["holes"]) == [4.7, 4.7]
    assert (job / "part.step").stat().st_size > 1000

    r = run("mesh_check.py", job)
    assert r.returncode == 0, r.stderr
    mc = json.loads((job / "mesh_check.json").read_text())
    assert mc["overhang_pct"] < 1.0  # teardrops and 45° chamfers sit exactly at the limit
    assert mc["bed_contact_area_mm2"] > 200

    r = run("render.py", job)
    assert r.returncode == 0, r.stderr
    for v in ("iso", "front", "right", "top", "bottom"):
        assert (job / "renders" / f"{v}.png").stat().st_size > 5000


def test_insert_mount_holes_exclude_bosses(job):
    shutil.copy(COOKBOOK / "insert_mount.py", job / "model.py")
    assert run("cad_build.py", job).returncode == 0
    geo = json.loads((job / "geometry.json").read_text())
    assert sorted(h["diameter"] for h in geo["holes"]) == [3.6, 4.1, 4.1, 4.1, 4.1]  # bosses are not holes


def test_cad_checks_template_runs(job):
    shutil.copy(COOKBOOK / "l_bracket.py", job / "model.py")
    shutil.copy(COOKBOOK / "cad_checks_template.txt", job / "cad_checks.py")
    tools_link = job.parents[1] / "tools"
    tools_link.symlink_to(ROOT / "tools")
    r = subprocess.run([sys.executable, str(job / "cad_checks.py")], capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.count("PASS") == 2


def test_cad_build_rejects_floating_part(job):
    (job / "model.py").write_text("from build123d import *\ndef build():\n    return Pos(0,0,10) * Box(10,10,10)\n")
    r = run("cad_build.py", job)
    assert r.returncode == 1 and "must be 0" in r.stderr


def test_cad_build_rejects_oversize(job):
    (job / "model.py").write_text(
        "from build123d import *\ndef build():\n    return Box(300,20,10, align=(Align.MIN,)*3)\n")
    r = run("cad_build.py", job)
    assert r.returncode == 1 and "does not fit" in r.stderr


def test_cad_build_reports_model_errors(job):
    (job / "model.py").write_text("def build():\n    raise RuntimeError('boom')\n")
    r = run("cad_build.py", job)
    assert r.returncode == 1 and "boom" in r.stderr


def test_mesh_check_flags_bridge_and_overhang(job):
    from build123d import Align, Box, Pos, export_stl
    # a table: two legs and a 40 mm unsupported top = bridge
    legs = Box(5, 20, 20, align=(Align.MIN,) * 3) + Pos(45, 0, 0) * Box(5, 20, 20, align=(Align.MIN,) * 3)
    top = Pos(0, 0, 20) * Box(50, 20, 3, align=(Align.MIN,) * 3)
    export_stl(legs + top, str(job / "part.stl"))
    assert run("mesh_check.py", job).returncode == 0
    mc = json.loads((job / "mesh_check.json").read_text())
    assert mc["bridges"] and mc["bridges"][0]["span_mm"] == pytest.approx(20, abs=0.5)
    assert mc["bridges"][0]["length_mm"] == pytest.approx(40, abs=0.5)
    assert mc["overhang_pct"] > 5
