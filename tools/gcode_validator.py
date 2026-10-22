#!/usr/bin/env python3
"""MK3 G-code validator. PROTECTED FILE: agents must not modify it.

Checks a plain-text G-code file against config/safety.json (hard machine and
safety limits) and, optionally, a job's print_requirements.json (engineering
settings the design needs).

Usage:
  python3 tools/gcode_validator.py <file.gcode> [--requirements <json>]
                                   [--safety <json>] [--out <json>]

Exit codes: 0 pass, 1 fail, 2 usage or I/O error.
The same `validate()` function is used by the approval tool and the
PreToolUse hook, so all three always agree.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

VERSION = "1.0.0"
ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SAFETY_PATH = ROOT / "config" / "safety.json"

FALLBACK_SAFETY = {
    "require_human_approval": True,
    "approval_max_age_hours": 24,
    "allowed_printer_models": ["MK3", "MK3S", "MK3MMU2", "MK3SMMU2S", "MK3SMMU3"],
    "nozzle_diameter": 0.4,
    "limits": {
        "max_nozzle_c": 300,
        "max_bed_c": 120,
        "x_mm": [-1.0, 255.0],
        "y_mm": [-4.0, 212.5],
        "z_mm": [0.0, 210.5],
        "max_print_hours": 48,
    },
    "forbidden_gcodes": ["M500", "M502", "M92", "M997", "M302"],
    "warn_gcodes": ["M907", "M350", "M906"],
    "require_heaters_off_at_end": True,
}

CMD_RE = re.compile(r"^([GMT])(\d+)(?:\.(\d+))?$")
PARAM_RE = re.compile(r"([A-Z])\s*([-+]?(?:\d+\.?\d*|\.\d+))")
MODEL_RE = re.compile(r'P\s*"?([A-Za-z0-9_+\-]+)"?')
TIME_RE = re.compile(r"(\d+)\s*([dhms])")
MAX_REPORTED_BOUND_ERRORS = 5


def load_json(path: Path | str | None, fallback: dict | None = None) -> dict:
    if path is None:
        return dict(fallback or {})
    p = Path(path)
    if not p.exists():
        if fallback is not None:
            return dict(fallback)
        raise FileNotFoundError(str(p))
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def load_safety(path: Path | str | None = None) -> dict:
    safety = json.loads(json.dumps(FALLBACK_SAFETY))
    p = Path(path) if path else DEFAULT_SAFETY_PATH
    if p.exists():
        user = load_json(p)
        for key, value in user.items():
            if key == "limits" and isinstance(value, dict):
                safety["limits"].update(value)
            else:
                safety[key] = value
    return safety


def sha256_file(path: Path | str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_duration(text: str) -> int | None:
    parts = TIME_RE.findall(text or "")
    if not parts:
        return None
    unit_s = {"d": 86400, "h": 3600, "m": 60, "s": 1}
    return sum(int(n) * unit_s[u] for n, u in parts)


def to_number(value) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().strip('"').rstrip("%").strip()
    # Multi-extruder values are comma-separated; use the first.
    text = text.split(",")[0].split(";")[0].strip()
    try:
        return float(text)
    except ValueError:
        return None


def norm_text(value) -> str:
    return str(value).strip().strip('"').strip().lower()


def validate(path: Path | str, safety: dict | None = None,
             requirements: dict | None = None) -> dict:
    safety = safety or load_safety()
    limits = safety["limits"]
    errors: list[str] = []
    warnings: list[str] = []
    result = {
        "file": str(path),
        "pass": False,
        "errors": errors,
        "warnings": warnings,
        "stats": {},
        "sha256": None,
        "validator_version": VERSION,
    }

    p = Path(path)
    if not p.exists():
        errors.append(f"File not found: {p}")
        return result
    if p.suffix.lower() == ".bgcode":
        errors.append("Binary G-code (.bgcode) is not allowed for the MK3; slice to plain .gcode.")
        return result
    with open(p, "rb") as f:
        head = f.read(4)
    if head == b"GCDE":
        errors.append("File is binary G-code; slice to plain-text .gcode.")
        return result

    result["sha256"] = sha256_file(p)

    forbidden = {c.upper() for c in safety.get("forbidden_gcodes", [])}
    warn_codes = {c.upper() for c in safety.get("warn_gcodes", [])}

    absolute_xyz = True
    relative_e = False
    last_e_abs = 0.0
    pos: dict[str, float | None] = {"X": None, "Y": None, "Z": None}
    seen = {a: [None, None] for a in "XYZ"}
    bound_errors = 0
    hotend_wait_seen = False
    extrusion_before_wait_reported = False
    extrusion_seen = False
    last_extrusion_line = 0
    nozzle_off_line = 0
    bed_off_line = 0
    max_nozzle = 0.0
    max_bed = 0.0
    model_check = None
    nozzle_check = None
    la_k_values: list[float] = []
    layer_count = 0
    generator = None
    comments: dict[str, str] = {}
    tool_changes = set()

    with open(p, encoding="utf-8", errors="replace") as f:
        for lineno, raw in enumerate(f, start=1):
            s = raw.strip()
            if not s:
                continue
            if s.startswith(";"):
                body = s[1:].strip()
                if body.lower().startswith("generated by"):
                    generator = body[len("generated by"):].strip()
                elif body.startswith("LAYER_CHANGE"):
                    layer_count += 1
                elif " = " in body:
                    key, _, value = body.partition(" = ")
                    comments[key.strip()] = value.strip()
                continue

            code = s.split(";", 1)[0].strip()
            if not code:
                continue
            first, _, rest = code.partition(" ")
            first = first.upper()
            m = CMD_RE.match(first)
            if not m:
                continue
            letter, num, sub = m.group(1), int(m.group(2)), m.group(3)
            cmd = f"{letter}{num}" + (f".{sub}" if sub else "")

            if letter == "T":
                tool_changes.add(num)
                continue

            if cmd in forbidden:
                errors.append(f"Line {lineno}: forbidden command {cmd} ({s[:60]})")
                continue
            if cmd in warn_codes:
                warnings.append(f"Line {lineno}: unusual command {cmd} ({s[:60]})")

            if cmd == "M862.3":
                mm = MODEL_RE.search(rest)
                model_check = mm.group(1) if mm else rest.strip()
                continue
            if cmd == "M862.1":
                params = dict(PARAM_RE.findall(rest.upper()))
                nozzle_check = to_number(params.get("P"))
                continue

            params = {k: float(v) for k, v in PARAM_RE.findall(rest.upper())}

            if cmd == "G90":
                absolute_xyz = True
            elif cmd == "G91":
                absolute_xyz = False
            elif cmd == "M82":
                relative_e = False
            elif cmd == "M83":
                relative_e = True
            elif cmd == "G92":
                for axis in "XYZ":
                    if axis in params:
                        pos[axis] = params[axis]
                if "E" in params:
                    last_e_abs = params["E"]
            elif cmd == "G28":
                homed = [a for a in "XYZ" if a in params] or list("XYZ")
                for axis in homed:
                    pos[axis] = None
            elif cmd in ("G0", "G1", "G2", "G3"):
                for axis in "XYZ":
                    if axis not in params:
                        continue
                    value = params[axis]
                    if absolute_xyz:
                        pos[axis] = value
                    elif pos[axis] is not None:
                        pos[axis] = pos[axis] + value
                    if pos[axis] is None:
                        continue
                    v = pos[axis]
                    lo_hi = seen[axis]
                    lo_hi[0] = v if lo_hi[0] is None else min(lo_hi[0], v)
                    lo_hi[1] = v if lo_hi[1] is None else max(lo_hi[1], v)
                    lo, hi = limits[f"{axis.lower()}_mm"]
                    if v < lo - 1e-6 or v > hi + 1e-6:
                        bound_errors += 1
                        if bound_errors <= MAX_REPORTED_BOUND_ERRORS:
                            errors.append(
                                f"Line {lineno}: {axis}={v:.3f} outside machine limits [{lo}, {hi}]")
                if "E" in params:
                    e = params["E"]
                    extruding = e > 0 if relative_e else e > last_e_abs
                    if not relative_e:
                        last_e_abs = e
                    if extruding:
                        extrusion_seen = True
                        last_extrusion_line = lineno
                        if not hotend_wait_seen and not extrusion_before_wait_reported:
                            errors.append(
                                f"Line {lineno}: extrusion before waiting for hotend temperature (M109)")
                            extrusion_before_wait_reported = True
            elif cmd in ("M104", "M109"):
                t = params.get("S", params.get("R"))
                if t is not None:
                    max_nozzle = max(max_nozzle, t)
                    if t > limits["max_nozzle_c"]:
                        errors.append(
                            f"Line {lineno}: nozzle {t:g} °C exceeds limit {limits['max_nozzle_c']} °C")
                    if t == 0:
                        nozzle_off_line = lineno
                    elif cmd == "M109":
                        hotend_wait_seen = True
            elif cmd in ("M140", "M190"):
                t = params.get("S", params.get("R"))
                if t is not None:
                    max_bed = max(max_bed, t)
                    if t > limits["max_bed_c"]:
                        errors.append(
                            f"Line {lineno}: bed {t:g} °C exceeds limit {limits['max_bed_c']} °C")
                    if t == 0:
                        bed_off_line = lineno
            elif cmd == "M900":
                if "K" in params:
                    la_k_values.append(params["K"])

    if bound_errors > MAX_REPORTED_BOUND_ERRORS:
        errors.append(f"... {bound_errors - MAX_REPORTED_BOUND_ERRORS} more out-of-bounds moves")

    allowed_models = [m.upper() for m in safety.get("allowed_printer_models", [])]
    if model_check is None:
        errors.append("Missing printer model check (M862.3). Slice with the Prusa MK3 printer profile.")
    elif model_check.upper() not in allowed_models:
        errors.append(f"Printer model '{model_check}' is not in allowed_printer_models {allowed_models}")

    expected_nozzle = to_number(safety.get("nozzle_diameter"))
    if nozzle_check is None:
        warnings.append("Missing nozzle diameter check (M862.1).")
    elif expected_nozzle is not None and abs(nozzle_check - expected_nozzle) > 1e-3:
        errors.append(f"G-code is for a {nozzle_check} mm nozzle; printer has {expected_nozzle} mm")

    if not extrusion_seen:
        errors.append("No extrusion moves found.")
    if not hotend_wait_seen and extrusion_seen and not extrusion_before_wait_reported:
        errors.append("No M109 (wait for hotend) before printing.")

    if safety.get("require_heaters_off_at_end", True) and extrusion_seen:
        if nozzle_off_line <= last_extrusion_line:
            errors.append("Hotend is not switched off (M104 S0) after the last extrusion.")
        if bed_off_line <= last_extrusion_line:
            errors.append("Bed is not switched off (M140 S0) after the last extrusion.")

    if sorted(tool_changes) not in ([], [0]) and "MMU" not in str(model_check).upper():
        warnings.append(f"Tool changes {sorted(tool_changes)} on a printer without MMU.")

    print_time_s = parse_duration(comments.get("estimated printing time (normal mode)", ""))
    stats = {
        "generator": generator,
        "printer_model_check": model_check,
        "nozzle_check_mm": nozzle_check,
        "print_time_s": print_time_s,
        "print_time_h": round(print_time_s / 3600, 2) if print_time_s else None,
        "filament_g": to_number(comments.get("filament used [g]")),
        "filament_mm": to_number(comments.get("filament used [mm]")),
        "filament_type": comments.get("filament_type"),
        "layer_height": to_number(comments.get("layer_height")),
        "perimeters": to_number(comments.get("perimeters")),
        "fill_density": to_number(comments.get("fill_density")),
        "fill_pattern": comments.get("fill_pattern"),
        "layers": layer_count,
        "max_nozzle_c": max_nozzle,
        "max_bed_c": max_bed,
        "la_k_values": sorted(set(la_k_values)),
        "extents_mm": {a: seen[a] for a in "XYZ"},
    }
    result["stats"] = stats

    max_hours = limits.get("max_print_hours")
    if print_time_s is None:
        warnings.append("No print time estimate found in G-code comments.")
    elif max_hours and print_time_s > max_hours * 3600:
        errors.append(f"Estimated print time {stats['print_time_h']} h exceeds safety limit {max_hours} h")

    if requirements:
        check_requirements(requirements, comments, stats, errors, warnings)

    result["pass"] = not errors
    return result


def check_requirements(req: dict, cfg: dict, stats: dict,
                       errors: list[str], warnings: list[str]) -> None:
    if "filament_type" in req:
        got = cfg.get("filament_type")
        if got is None:
            errors.append("Requirement filament_type: no filament_type in G-code config block.")
        elif norm_text(req["filament_type"]) not in [norm_text(x) for x in re.split(r"[;,]", got)]:
            errors.append(f"Requirement filament_type={req['filament_type']}, G-code has {got}")

    if "nozzle_diameter" in req:
        got = to_number(cfg.get("nozzle_diameter"))
        if got is None or abs(got - float(req["nozzle_diameter"])) > 1e-3:
            errors.append(f"Requirement nozzle_diameter={req['nozzle_diameter']}, G-code has {got}")

    for key, minimum in (req.get("min") or {}).items():
        got = to_number(cfg.get(key))
        if got is None:
            errors.append(f"Requirement min {key}: setting not found in G-code config block.")
        elif got < float(minimum) - 1e-9:
            errors.append(f"Requirement {key} >= {minimum}, G-code has {got:g}")

    for key, maximum in (req.get("max") or {}).items():
        got = to_number(cfg.get(key))
        if got is None:
            errors.append(f"Requirement max {key}: setting not found in G-code config block.")
        elif got > float(maximum) + 1e-9:
            errors.append(f"Requirement {key} <= {maximum}, G-code has {got:g}")

    for key, expected in (req.get("equals") or {}).items():
        got = cfg.get(key)
        if got is None:
            errors.append(f"Requirement {key} == {expected}: setting not found in G-code config block.")
            continue
        num_exp, num_got = to_number(expected), to_number(got)
        same = (abs(num_exp - num_got) < 1e-9) if (num_exp is not None and num_got is not None) \
            else norm_text(expected).rstrip("%") == norm_text(got).rstrip("%")
        if not same:
            errors.append(f"Requirement {key} == {expected}, G-code has {got}")

    for req_key, cfg_keys, stat_key in (
        ("nozzle_temp_c", ("temperature", "first_layer_temperature"), "max_nozzle_c"),
        ("bed_temp_c", ("bed_temperature", "first_layer_bed_temperature"), "max_bed_c"),
    ):
        if req_key not in req:
            continue
        lo, hi = (float(v) for v in req[req_key])
        for ck in cfg_keys:
            got = to_number(cfg.get(ck))
            if got is None:
                warnings.append(f"Requirement {req_key}: {ck} not found in G-code config block.")
            elif not lo <= got <= hi:
                errors.append(f"Requirement {req_key} in [{lo:g}, {hi:g}], {ck} is {got:g}")
        if stats.get(stat_key) and stats[stat_key] > hi:
            errors.append(f"Requirement {req_key}: G-code sets {stats[stat_key]:g} °C, above {hi:g}")

    if "max_print_hours" in req and stats.get("print_time_s"):
        if stats["print_time_s"] > float(req["max_print_hours"]) * 3600:
            errors.append(
                f"Requirement max_print_hours={req['max_print_hours']}, estimate is {stats['print_time_h']} h")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Validate MK3 G-code against safety limits and job requirements.")
    ap.add_argument("gcode")
    ap.add_argument("--requirements", help="print_requirements.json for the job")
    ap.add_argument("--safety", help="safety.json (default: config/safety.json)")
    ap.add_argument("--out", help="write the JSON result to this file")
    args = ap.parse_args(argv)

    if args.out and Path(args.out).name == "approval.json":
        print("Refusing to write to approval.json", file=sys.stderr)
        return 2
    try:
        safety = load_safety(args.safety)
        requirements = load_json(args.requirements) if args.requirements else None
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Could not read configuration: {exc}", file=sys.stderr)
        return 2

    result = validate(args.gcode, safety, requirements)
    text = json.dumps(result, indent=2)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
        verdict = "PASS" if result["pass"] else "FAIL"
        print(f"{verdict}: {len(result['errors'])} errors, {len(result['warnings'])} warnings -> {args.out}")
        for err in result["errors"]:
            print(f"  ERROR: {err}")
    else:
        print(text)
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
