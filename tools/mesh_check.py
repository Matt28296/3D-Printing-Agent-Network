#!/usr/bin/env python3
"""Printability checks on a job's mesh: python3 tools/mesh_check.py jobs/<id> [--overhang-deg 45]

Writes mesh_check.json:
  overhang_area_mm2, overhang_pct   downward faces steeper than the limit (measured
                                    from vertical), excluding faces on the bed
  bed_contact_area_mm2              area touching Z = 0
  bridges                           horizontal ceilings above the bed: span (short
                                    side) and length of each region, mm
  thin_wall_warnings                approximate: sampled wall thickness under 0.9 mm
  bbox_mm, fits_bed
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
BED_EPS = 0.2
THIN_MM = 0.9


def bed_size():
    try:
        return json.loads((ROOT / "config" / "printer.json").read_text()).get("bed_mm", [250, 210, 210])
    except (OSError, json.JSONDecodeError):
        return [250, 210, 210]


def check(job: Path, overhang_deg: float = 45.0, samples: int = 1500) -> dict:
    import trimesh

    mesh = trimesh.load(job / "part.stl", force="mesh")
    n = mesh.face_normals
    areas = mesh.area_faces
    zmin_face = mesh.triangles[:, :, 2].min(axis=1)
    zmax_face = mesh.triangles[:, :, 2].max(axis=1)
    on_bed = zmax_face < BED_EPS

    limit = math.cos(math.radians(overhang_deg))  # -n_z above this = steeper than limit from vertical
    overhang = (-n[:, 2] > limit + 0.01) & ~on_bed  # faces at exactly the limit (45° chamfers, teardrops) pass
    contact = (n[:, 2] < -0.99) & (zmax_face < 0.05)

    bridges = []
    flat_down = np.where((n[:, 2] < -0.99) & (zmin_face > BED_EPS))[0]
    if len(flat_down):
        adj = mesh.face_adjacency
        mask = np.isin(adj, flat_down).all(axis=1)
        groups = trimesh.graph.connected_components(adj[mask], nodes=flat_down)
        for g in groups:
            pts = mesh.triangles[g].reshape(-1, 3)
            _, extents = trimesh.bounds.oriented_bounds_2D(pts[:, :2])
            span, length = sorted(float(e) for e in extents)
            bridges.append({"z_mm": round(float(pts[:, 2].mean()), 2), "span_mm": round(span, 2),
                            "length_mm": round(length, 2), "area_mm2": round(float(areas[g].sum()), 1)})
        bridges.sort(key=lambda b: -b["span_mm"])

    thin = []
    try:
        rng = np.random.default_rng(0)
        prob = areas / areas.sum()
        idx = rng.choice(len(areas), size=min(samples, len(areas)), replace=False, p=prob)
        origins = mesh.triangles_center[idx] - n[idx] * 1e-4
        locs, ray_idx, _ = mesh.ray.intersects_location(origins, -n[idx], multiple_hits=False)
        dist = np.full(len(idx), np.inf)
        dist[ray_idx] = np.linalg.norm(locs - origins[ray_idx], axis=1)
        for k in np.where(dist < THIN_MM)[0][:20]:
            c = mesh.triangles_center[idx[k]]
            thin.append({"at_mm": [round(float(v), 1) for v in c], "thickness_mm": round(float(dist[k]), 2)})
    except Exception as exc:  # ray backend missing: report, don't fail
        thin = [{"note": f"thin-wall check unavailable: {exc}"}]

    lo, hi = mesh.bounds
    size = (hi - lo).tolist()
    bed = bed_size()
    total = float(areas.sum())
    return {
        "overhang_limit_deg": overhang_deg,
        "overhang_area_mm2": round(float(areas[overhang].sum()), 1),
        "overhang_pct": round(100 * float(areas[overhang].sum()) / total, 2) if total else 0.0,
        "bed_contact_area_mm2": round(float(areas[contact].sum()), 1),
        "bridges": bridges[:20],
        "thin_wall_warnings": thin,
        "bbox_mm": [round(v, 2) for v in size],
        "fits_bed": bool(size[0] <= bed[0] - 10 and size[1] <= bed[1] - 10 and size[2] <= bed[2]),
        "watertight": bool(mesh.is_watertight),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Printability checks for jobs/<id>/part.stl.")
    ap.add_argument("job")
    ap.add_argument("--overhang-deg", type=float, default=45.0)
    args = ap.parse_args(argv)
    job = Path(args.job).resolve()
    if not (job / "part.stl").exists():
        print(f"No part.stl in {job}; run tools/cad_build.py first.", file=sys.stderr)
        return 2
    result = check(job, args.overhang_deg)
    (job / "mesh_check.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    widest = result["bridges"][0]["span_mm"] if result["bridges"] else 0
    print(f"overhang {result['overhang_pct']}% · bed contact {result['bed_contact_area_mm2']} mm² · "
          f"widest bridge {widest} mm · thin-wall hits {len([t for t in result['thin_wall_warnings'] if 'at_mm' in t])}"
          f" · fits bed {result['fits_bed']} -> mesh_check.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
