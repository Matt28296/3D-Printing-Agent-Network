#!/usr/bin/env python3
"""Build a job's CAD model and export it: python3 tools/cad_build.py jobs/<id> [--timeout 300]

Runs jobs/<id>/model.py in a separate Python process (the job folder is the
working directory, tools/ is importable so `from cadlib import *` works),
calls build(), exports part.step and part.stl, and writes geometry.json.
Exit 0 when the part is a single watertight solid on the bed that fits.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
DEFAULT_BED = [250, 210, 210]
MARGIN = 5.0

CHILD = r"""
import json, runpy, sys
sys.path.insert(0, sys.argv[1])
from build123d import export_step, export_stl, Compound
from cadlib import measure_holes
ns = runpy.run_path("model.py", run_name="model")
if "build" not in ns or not callable(ns["build"]):
    sys.exit("model.py must define build() returning a build123d Part")
part = ns["build"]()
if hasattr(part, "part") and not hasattr(part, "volume"):
    part = part.part  # a BuildPart context was returned
solids = part.solids()
bb = part.bounding_box()
export_step(part, "part.step")
export_stl(part, "part.stl", tolerance=0.01, angular_tolerance=0.1)
try:
    holes = measure_holes(part)
except Exception as exc:
    holes = {"error": str(exc)}
print(json.dumps({
    "bbox_mm": [round(bb.size.X, 3), round(bb.size.Y, 3), round(bb.size.Z, 3)],
    "bbox_min_mm": [round(bb.min.X, 3), round(bb.min.Y, 3), round(bb.min.Z, 3)],
    "volume_mm3": round(part.volume, 2),
    "area_mm2": round(part.area, 2),
    "solids": len(solids),
    "holes": holes,
}))
"""


def bed_size() -> list[float]:
    cfg = ROOT / "config" / "printer.json"
    try:
        return json.loads(cfg.read_text()).get("bed_mm", DEFAULT_BED)
    except (OSError, json.JSONDecodeError):
        return DEFAULT_BED


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Build jobs/<id>/model.py and export STEP/STL.")
    ap.add_argument("job")
    ap.add_argument("--timeout", type=int, default=300)
    args = ap.parse_args(argv)

    job = Path(args.job).resolve()
    if not (job / "model.py").exists():
        print(f"No model.py in {job}", file=sys.stderr)
        return 2
    for stale in ("part.step", "part.stl", "geometry.json"):
        (job / stale).unlink(missing_ok=True)

    try:
        proc = subprocess.run([sys.executable, "-c", CHILD, str(TOOLS)], cwd=job,
                              capture_output=True, text=True, timeout=args.timeout)
    except subprocess.TimeoutExpired:
        print(f"model.py did not finish within {args.timeout} s. Simplify the geometry or raise --timeout.",
              file=sys.stderr)
        return 1
    if proc.returncode != 0:
        print("model.py failed:\n" + (proc.stderr.strip()[-3000:] or proc.stdout[-3000:]), file=sys.stderr)
        return 1
    try:
        geo = json.loads(proc.stdout.strip().splitlines()[-1])
    except (IndexError, json.JSONDecodeError):
        print("Could not read build output:\n" + proc.stdout[-2000:], file=sys.stderr)
        return 1

    import trimesh  # imported late so --help works without it
    mesh = trimesh.load(job / "part.stl", force="mesh")
    bed = bed_size()
    fits = (geo["bbox_mm"][0] <= bed[0] - 2 * MARGIN and geo["bbox_mm"][1] <= bed[1] - 2 * MARGIN
            and geo["bbox_mm"][2] <= bed[2])
    geo.update({
        "min_z_mm": geo["bbox_min_mm"][2],
        "watertight": bool(mesh.is_watertight),
        "mesh_faces": int(len(mesh.faces)),
        "fits_bed": bool(fits),
        "bed_mm": bed,
        "margin_mm": MARGIN,
    })
    (job / "geometry.json").write_text(json.dumps(geo, indent=2) + "\n", encoding="utf-8")

    problems = []
    if geo["solids"] < 1:
        problems.append("no solid produced")
    if abs(geo["min_z_mm"]) > 0.01:
        problems.append(f"lowest point is Z={geo['min_z_mm']}, must be 0 (model in print orientation on the bed)")
    if not geo["watertight"]:
        problems.append("exported mesh is not watertight")
    if not fits:
        problems.append(f"part {geo['bbox_mm']} does not fit the bed {bed} with {MARGIN} mm margin")
    summary = f"bbox {geo['bbox_mm']} mm, volume {geo['volume_mm3']} mm³, solids {geo['solids']}, holes {len(geo['holes']) if isinstance(geo['holes'], list) else '?'}"
    if problems:
        print("FAIL: " + "; ".join(problems) + f" ({summary})", file=sys.stderr)
        return 1
    print(f"OK: {summary} -> part.step, part.stl, geometry.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
