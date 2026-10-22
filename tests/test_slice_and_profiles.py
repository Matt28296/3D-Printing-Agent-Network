"""vendor_profiles (always) and slice.py (only when PrusaSlicer is installed)."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import vendor_profiles as vp  # noqa: E402

BUNDLE = """[vendor]
name = Prusa Research
config_version = 9.9.9

[printer:*common*]
bed_shape = 0x0,250x0,250x210,0x210
gcode_flavor = marlin
[printer:*mk3*]
inherits = *common*
printer_model = MK3S
nozzle_diameter = 0.4
[printer:Original Prusa i3 MK3S & MK3S+]
inherits = *mk3*
printer_notes = PRINTER_MODEL_MK3S

[filament:*PET*]
temperature = 240
bed_temperature = 90
[filament:Prusament PETG]
inherits = *PET*
filament_type = PETG
bed_temperature = 85
"""


def test_vendor_profile_resolves_inheritance(tmp_path):
    bundle = tmp_path / "PrusaResearch.ini"
    bundle.write_text(BUNDLE)
    out = tmp_path / "profiles"
    assert vp.main(["--bundle", str(bundle), "--printer", "Original Prusa i3 MK3S & MK3S+",
                    "--filament", "Prusament PETG", "--out", str(out)]) == 0
    printer = (out / "printer" / "Original_Prusa_i3_MK3S_MK3S+.ini").read_text()
    assert "printer_model = MK3S" in printer and "bed_shape = 0x0,250x0,250x210,0x210" in printer
    assert "inherits" not in printer.split("\n", 3)[3]
    fil = (out / "filament" / "Prusament_PETG.ini").read_text()
    assert "bed_temperature = 85" in fil and "temperature = 240" in fil  # own value overrides parent
    assert vp.list_presets(vp.parse_bundle(bundle)[0], "printer", None) == ["Original Prusa i3 MK3S & MK3S+"]


def test_vendor_profile_unknown_name(tmp_path, capsys):
    bundle = tmp_path / "PrusaResearch.ini"
    bundle.write_text(BUNDLE)
    assert vp.main(["--bundle", str(bundle), "--filament", "Nope PLA", "--out", str(tmp_path)]) == 1


import slice as slicer  # noqa: E402


def test_slice_refuses_custom_gcode_keys():
    for k in ("start_gcode", "end_gcode", "before_layer_gcode", "post_process", "printer_notes",
              "machine_max_feedrate_x", "binary_gcode", "bed_shape", "printhost_apikey"):
        assert slicer.refused(k), k
    for k in ("perimeters", "fill_density", "temperature", "extrusion_multiplier", "seam_position"):
        assert not slicer.refused(k), k


def _prusaslicer():
    try:
        return slicer.find_prusaslicer({})
    except FileNotFoundError:
        return None


def _bundle():
    for p in vp.candidate_bundles():
        if p.exists():
            return p
    return None


@pytest.mark.integration
@pytest.mark.skipif(_prusaslicer() is None or _bundle() is None, reason="PrusaSlicer not installed")
def test_real_slice_passes_validator(tmp_path):
    import gcode_validator as gv
    prof = tmp_path / "profiles"
    assert vp.main(["--printer", "Original Prusa i3 MK3S & MK3S+", "--print", "0.20mm QUALITY @MK3",
                    "--filament", "Prusament PETG", "--out", str(prof)]) == 0
    job = ROOT / "jobs" / "_pytest_slice"
    shutil.rmtree(job, ignore_errors=True)
    job.mkdir(parents=True)
    try:
        shutil.copy(ROOT / "tests" / "fixtures" / "cube20.stl", job / "part.stl")
        plan = {"printer_profile": str(prof / "printer" / "Original_Prusa_i3_MK3S_MK3S+.ini"),
                "print_profile": str(prof / "print" / "0.20mm_QUALITY_@MK3.ini"),
                "filament_profile": str(prof / "filament" / "Prusament_PETG.ini"),
                "overrides": {"perimeters": 5, "fill_density": "40%", "fill_pattern": "gyroid"},
                "model": "part.stl", "copies": 2}
        (job / "slice_plan.json").write_text(json.dumps(plan))
        r = subprocess.run([sys.executable, str(ROOT / "tools" / "slice.py"), str(job)],
                           capture_output=True, text=True, timeout=600)
        assert r.returncode == 0, r.stderr
        req = {"filament_type": "PETG", "min": {"perimeters": 5, "fill_density": 40},
               "equals": {"fill_pattern": "gyroid"}}
        result = gv.validate(job / "part.gcode", gv.load_safety(), req)
        assert result["pass"], result["errors"]
        stats = json.loads((job / "slice_stats.json").read_text())
        assert stats["filament_type"] == "PETG" and stats["perimeters"] == 5 and stats["print_time_s"] > 0
    finally:
        shutil.rmtree(job, ignore_errors=True)
