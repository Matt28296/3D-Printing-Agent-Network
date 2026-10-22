import json

import gcode_validator as gv

SAFETY = gv.load_safety()
REQ = {
    "filament_type": "PETG",
    "nozzle_diameter": 0.4,
    "min": {"perimeters": 4, "top_solid_layers": 6, "bottom_solid_layers": 5, "fill_density": 40},
    "max": {"layer_height": 0.2},
    "equals": {"fill_pattern": "gyroid"},
    "nozzle_temp_c": [225, 250],
    "bed_temp_c": [80, 95],
    "max_print_hours": 8,
}


def errors_of(path, req=None):
    return gv.validate(path, SAFETY, req)["errors"]


def test_good_file_passes_with_requirements(make_gcode):
    r = gv.validate(make_gcode(), SAFETY, REQ)
    assert r["pass"], r["errors"]
    st = r["stats"]
    assert st["print_time_s"] == 3723
    assert st["filament_g"] == 1.57
    assert st["perimeters"] == 4 and st["fill_density"] == 40
    assert st["max_nozzle_c"] == 240 and st["max_bed_c"] == 90
    assert st["layers"] == 2
    assert st["extents_mm"]["Y"][0] == -3
    assert len(r["sha256"]) == 64


def test_missing_model_check_fails(make_gcode):
    p = make_gcode()
    p.write_text(p.read_text().replace('M862.3 P "MK3S" ; printer model check\n', ""))
    assert any("M862.3" in e for e in errors_of(p))


def test_wrong_printer_model_fails(make_gcode):
    assert any("not in allowed" in e for e in errors_of(make_gcode(model="MK4S")))


def test_wrong_nozzle_fails(make_gcode):
    assert any("0.6 mm nozzle" in e for e in errors_of(make_gcode(nozzle="0.6")))


def test_nozzle_over_limit_fails(make_gcode):
    assert any("exceeds limit 300" in e for e in errors_of(make_gcode(temp=310)))


def test_bed_over_limit_fails(make_gcode):
    assert any("exceeds limit 120" in e for e in errors_of(make_gcode(bed=125)))


def test_out_of_bounds_move_fails(make_gcode):
    assert any("X=300.000" in e for e in errors_of(make_gcode(far_x=300)))


def test_extrusion_before_m109_fails(make_gcode):
    errs = errors_of(make_gcode(wait_line="; no wait"))
    assert any("before waiting for hotend" in e for e in errs)


def test_forbidden_command_fails(make_gcode):
    assert any("M500" in e for e in errors_of(make_gcode(extra="M500 ; save settings")))


def test_warn_command_only_warns(make_gcode):
    r = gv.validate(make_gcode(extra="M907 E538"), SAFETY)
    assert r["pass"] and any("M907" in w for w in r["warnings"])


def test_heaters_left_on_fails(make_gcode):
    errs = errors_of(make_gcode(nozzle_off="", bed_off=""))
    assert any("Hotend is not switched off" in e for e in errs)
    assert any("Bed is not switched off" in e for e in errs)


def test_safety_time_limit(make_gcode):
    assert any("exceeds safety limit" in e for e in errors_of(make_gcode(time="2d 1h 0m 0s")))


def test_requirement_perimeters(make_gcode):
    assert any("perimeters >= 5" in e for e in errors_of(make_gcode(), {**REQ, "min": {"perimeters": 5}}))


def test_requirement_filament_type(make_gcode):
    assert any("filament_type" in e for e in errors_of(make_gcode(ftype="PLA"), REQ))


def test_requirement_fill_density_percent(make_gcode):
    assert any("fill_density >= 40" in e for e in errors_of(make_gcode(fill="25%"), REQ))


def test_requirement_temperature_range(make_gcode):
    assert any("nozzle_temp_c" in e for e in errors_of(make_gcode(temp=255), REQ))


def test_requirement_missing_setting(make_gcode):
    req = {"min": {"support_material_contact_distance": 0.1}}
    assert any("not found" in e for e in errors_of(make_gcode(), req))


def test_binary_gcode_rejected(tmp_path):
    p = tmp_path / "part.gcode"
    p.write_bytes(b"GCDE\x01\x00\x00\x00")
    assert any("binary" in e.lower() for e in errors_of(p))


def test_parse_duration():
    assert gv.parse_duration("1d 2h 3m 4s") == 93784
    assert gv.parse_duration("45m 10s") == 2710
    assert gv.parse_duration("") is None


def test_cli_refuses_to_write_approval(make_gcode, tmp_path):
    p = make_gcode()
    assert gv.main([str(p), "--out", str(tmp_path / "approval.json")]) == 2


def test_cli_writes_out_file(make_gcode, tmp_path):
    p = make_gcode()
    out = tmp_path / "validation.json"
    assert gv.main([str(p), "--out", str(out)]) == 0
    assert json.loads(out.read_text())["pass"] is True
