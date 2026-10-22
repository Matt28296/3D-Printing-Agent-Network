#!/usr/bin/env python3
"""Slice a job with the PrusaSlicer CLI: python3 tools/slice.py jobs/<id> [--plan jobs/<id>/slice_plan.json]

slice_plan.json:
  {"printer_profile": "profiles/printer/....ini",
   "print_profile": "profiles/print/....ini",
   "filament_profile": "profiles/filament/....ini",
   "overrides": {"perimeters": 5, "fill_density": "50%", "fill_pattern": "gyroid"},
   "model": "part.stl", "copies": 1, "rationale": "..."}

Overrides are written to slice_overrides.ini and loaded after the profiles, so
they win. Keys are checked against the installed PrusaSlicer's option list;
custom G-code, post-processing, machine geometry/limits and print-host keys are
refused. Output is always plain-text G-code. Writes part.gcode,
slice_settings.json and slice_stats.json.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

REFUSED_EXACT = {"post_process", "binary_gcode", "bed_shape", "max_print_height", "nozzle_diameter",
                 "printer_model", "printer_technology", "gcode_flavor", "output_filename_format",
                 "host_type", "print_host", "printhost_apikey", "printhost_cafile"}
REFUSED_PATTERNS = [re.compile(p) for p in (r"gcode", r"^machine_", r"^printhost", r"_notes$", r"^thumbnails")]


def load_printer_cfg() -> dict:
    try:
        return json.loads((ROOT / "config" / "printer.json").read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def find_prusaslicer(cfg: dict) -> str:
    candidates = [os.environ.get("PRUSASLICER"), cfg.get("prusaslicer_path"), "prusa-slicer",
                  "prusa-slicer-console", "PrusaSlicer"]
    for c in candidates:
        if not c:
            continue
        if Path(c).exists():
            return str(c)
        found = shutil.which(c)
        if found:
            return found
    raise FileNotFoundError("PrusaSlicer CLI not found. Set prusaslicer_path in config/printer.json "
                            "(macOS: /Applications/PrusaSlicer.app/Contents/MacOS/PrusaSlicer; "
                            "Windows: C:\\Program Files\\Prusa3D\\PrusaSlicer\\prusa-slicer-console.exe).")


def known_options(ps: str) -> set[str]:
    out = subprocess.run([ps, "--help-fff"], capture_output=True, text=True, timeout=60).stdout
    return {m.group(1).replace("-", "_") for m in re.finditer(r"^\s+--([a-z0-9][a-z0-9-]*)", out, re.M)}


def ps_version(ps: str) -> str:
    out = subprocess.run([ps, "--help"], capture_output=True, text=True, timeout=60).stdout
    return out.splitlines()[0].strip() if out else "unknown"


def refused(key: str) -> bool:
    return key in REFUSED_EXACT or any(p.search(key) for p in REFUSED_PATTERNS)


def ini_value(v) -> str:
    if isinstance(v, bool):
        return "1" if v else "0"
    return str(v)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Slice jobs/<id> with PrusaSlicer according to slice_plan.json.")
    ap.add_argument("job")
    ap.add_argument("--plan")
    ap.add_argument("--timeout", type=int, default=900)
    args = ap.parse_args(argv)

    job = Path(args.job).resolve()
    plan_path = Path(args.plan).resolve() if args.plan else job / "slice_plan.json"
    try:
        plan = json.loads(plan_path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Cannot read slice plan {plan_path}: {exc}", file=sys.stderr)
        return 2

    profiles = []
    for key in ("printer_profile", "print_profile", "filament_profile"):
        p = (ROOT / plan.get(key, "")).resolve() if plan.get(key) else None
        if not p or not p.is_file():
            print(f"{key} missing or not found: {plan.get(key)}", file=sys.stderr)
            return 2
        profiles.append(p)
    model = job / plan.get("model", "part.stl")
    if not model.exists():
        print(f"Model not found: {model}", file=sys.stderr)
        return 2

    cfg = load_printer_cfg()
    try:
        ps = find_prusaslicer(cfg)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    options = known_options(ps)

    overrides = plan.get("overrides") or {}
    bad = sorted(k for k in overrides if refused(k))
    if bad:
        print(f"Refused override keys (custom G-code, machine or host settings): {bad}", file=sys.stderr)
        return 2
    unknown = sorted(k for k in overrides if k not in options)
    if unknown:
        print(f"Unknown PrusaSlicer option(s) for {ps_version(ps)}: {unknown}. "
              f"Check names with `{ps} --help-fff`.", file=sys.stderr)
        return 2

    ov_path = job / "slice_overrides.ini"
    lines = ["# Written by tools/slice.py from slice_plan.json; loaded after the profiles."]
    lines += [f"{k} = {ini_value(v)}" for k, v in overrides.items()]
    if "binary_gcode" in options:
        lines.append("binary_gcode = 0")
    ov_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    bed = cfg.get("bed_mm", [250, 210, 210])
    out = job / "part.gcode"
    out.unlink(missing_ok=True)
    cmd = [ps, "--export-gcode"]
    for p in profiles + [ov_path]:
        cmd += ["--load", str(p)]
    copies = int(plan.get("copies", 1))
    if copies > 1:
        cmd += ["--duplicate", str(copies)]  # PrusaSlicer arranges copies on the bed itself
    else:
        cmd += ["--center", f"{bed[0] / 2:g},{bed[1] / 2:g}"]
    cmd += [str(model), "--output", str(out)]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=args.timeout)
    except subprocess.TimeoutExpired:
        print(f"PrusaSlicer did not finish within {args.timeout} s.", file=sys.stderr)
        return 1
    if proc.returncode != 0 or not out.exists():
        tail = (proc.stderr or proc.stdout).strip()[-3000:]
        print(f"PrusaSlicer failed (exit {proc.returncode}):\n{tail}", file=sys.stderr)
        return 1
    with open(out, "rb") as f:
        if f.read(4) == b"GCDE":
            print("PrusaSlicer produced binary G-code; the MK3 needs plain text.", file=sys.stderr)
            return 1

    import gcode_validator as gv
    stats = gv.validate(out)["stats"]
    rel = lambda p: str(p.relative_to(ROOT)) if ROOT in p.parents else str(p)  # noqa: E731
    settings = {
        "prusaslicer": ps_version(ps),
        "command": [rel(Path(c)) if os.path.isabs(c) else c for c in cmd],
        "profiles": {rel(p): sha256(p) for p in profiles},
        "overrides": overrides,
        "copies": copies,
        "warnings": [ln for ln in (proc.stderr or "").splitlines() if "warn" in ln.lower()][:20],
    }
    (job / "slice_settings.json").write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
    slice_stats = {
        "print_time_s": stats["print_time_s"],
        "print_time_h": stats["print_time_h"],
        "filament_g": stats["filament_g"],
        "filament_mm": stats["filament_mm"],
        "layers": stats["layers"],
        "max_z_mm": (stats["extents_mm"]["Z"] or [None, None])[1],
        "filament_type": stats["filament_type"],
        "nozzle_temp_c": stats["max_nozzle_c"],
        "bed_temp_c": stats["max_bed_c"],
        "layer_height": stats["layer_height"],
        "perimeters": stats["perimeters"],
        "fill_density": stats["fill_density"],
        "fill_pattern": stats["fill_pattern"],
    }
    (job / "slice_stats.json").write_text(json.dumps(slice_stats, indent=2) + "\n", encoding="utf-8")
    print(f"OK: {slice_stats['print_time_h']} h, {slice_stats['filament_g']} g {slice_stats['filament_type']}, "
          f"{slice_stats['layers']} layers -> part.gcode, slice_stats.json, slice_settings.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
