#!/usr/bin/env python3
"""Render review images of a job's part: python3 tools/render.py jobs/<id>

Writes renders/iso.png, front.png, right.png, top.png and bottom.png
(800 x 800) from part.stl with a small z-buffer rasterizer (headless, no
OpenGL), so hidden faces never show through. Each view shows the bed at
Z = 0 with a 10 mm grid, the part's feature edges, an XYZ axis triad and the
bounding-box size, so reviewers can judge orientation and proportions from
the images alone.
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

SIZE = 800
VIEWS = {  # name: (elevation, azimuth) in degrees, matplotlib convention
    "iso": (28, -55),
    "front": (0, -90),
    "right": (0, 0),
    "top": (90, -90),
    "bottom": (-90, -90),
}
PART_RGB = np.array([0.25, 0.50, 0.78])
BED_RGB = np.array([0.88, 0.88, 0.88])
EDGE_RGB = np.array([0.12, 0.14, 0.18])
GRID_RGB = np.array([0.70, 0.70, 0.70])


def camera(elev: float, azim: float) -> np.ndarray:
    e, a = math.radians(elev), math.radians(azim)
    d = np.array([math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)])
    if abs(d[2]) > 0.999:
        right = np.array([1.0, 0.0, 0.0])
    else:
        right = np.cross([0.0, 0.0, 1.0], d)
        right /= np.linalg.norm(right)
    up = np.cross(d, right)
    return np.vstack([right, up, d])  # rows: screen x, screen y, toward viewer


def rasterize(tris, colors, img, zbuf):
    h, w = zbuf.shape
    for t, col in zip(tris, colors):
        xs, ys, zs = t[:, 0], t[:, 1], t[:, 2]
        x0, x1 = max(int(math.floor(xs.min())), 0), min(int(math.ceil(xs.max())), w - 1)
        y0, y1 = max(int(math.floor(ys.min())), 0), min(int(math.ceil(ys.max())), h - 1)
        if x0 > x1 or y0 > y1:
            continue
        area = (xs[1] - xs[0]) * (ys[2] - ys[0]) - (xs[2] - xs[0]) * (ys[1] - ys[0])
        if abs(area) < 1e-12:
            continue
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        w0 = ((xs[1] - gx) * (ys[2] - gy) - (xs[2] - gx) * (ys[1] - gy)) / area
        w1 = ((xs[2] - gx) * (ys[0] - gy) - (xs[0] - gx) * (ys[2] - gy)) / area
        w2 = 1.0 - w0 - w1
        inside = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
        if not inside.any():
            continue
        z = w0 * zs[0] + w1 * zs[1] + w2 * zs[2]
        sub = zbuf[y0:y1 + 1, x0:x1 + 1]
        m = inside & (z > sub)
        sub[m] = z[m]
        img[y0:y1 + 1, x0:x1 + 1][m] = col


def draw_lines(segs, rgb, img, zbuf, eps):
    h, w = zbuf.shape
    for a, b in segs:
        n = max(2, int(np.hypot(*(b[:2] - a[:2]))) * 2)
        t = np.linspace(0, 1, n)[:, None]
        p = a + (b - a) * t
        xi, yi = p[:, 0].astype(int), p[:, 1].astype(int)
        ok = (xi >= 0) & (xi < w) & (yi >= 0) & (yi < h)
        xi, yi, z = xi[ok], yi[ok], p[ok, 2]
        vis = z >= zbuf[yi, xi] - eps
        img[yi[vis], xi[vis]] = rgb


def render_view(mesh, elev, azim, with_bed=True):
    R = camera(elev, azim)
    lo, hi = mesh.bounds
    pad = max(hi - lo) * 0.12 + 3
    bed_lo = np.floor((lo[:2] - pad) / 10) * 10
    bed_hi = np.ceil((hi[:2] + pad) / 10) * 10

    verts = mesh.vertices @ R.T
    corners = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
    if with_bed:
        corners = np.vstack([corners, [[bed_lo[0], bed_lo[1], 0], [bed_hi[0], bed_hi[1], 0],
                                       [bed_lo[0], bed_hi[1], 0], [bed_hi[0], bed_lo[1], 0]]])
    cv = corners @ R.T
    vmin, vmax = cv.min(axis=0), cv.max(axis=0)
    scale = (SIZE * 0.86) / max(vmax[0] - vmin[0], vmax[1] - vmin[1], 1e-6)
    off = (SIZE - (vmax[:2] - vmin[:2]) * scale) / 2

    def to_px(v):
        out = np.empty_like(v)
        out[..., 0] = (v[..., 0] - vmin[0]) * scale + off[0]
        out[..., 1] = SIZE - ((v[..., 1] - vmin[1]) * scale + off[1])
        out[..., 2] = v[..., 2]
        return out

    img = np.ones((SIZE, SIZE, 3))
    zbuf = np.full((SIZE, SIZE), -np.inf)

    if with_bed:
        bz = -0.02
        quad = np.array([[bed_lo[0], bed_lo[1], bz], [bed_hi[0], bed_lo[1], bz],
                         [bed_hi[0], bed_hi[1], bz], [bed_lo[0], bed_hi[1], bz]])
        q = to_px(quad @ R.T)
        if R[2, 2] > 0.02:  # bed is visible from above
            rasterize(np.array([q[[0, 1, 2]], q[[0, 2, 3]]]), [BED_RGB, BED_RGB], img, zbuf)
            grid = []
            for x in np.arange(bed_lo[0], bed_hi[0] + 0.1, 10):
                grid.append((np.array([x, bed_lo[1], bz]), np.array([x, bed_hi[1], bz])))
            for y in np.arange(bed_lo[1], bed_hi[1] + 0.1, 10):
                grid.append((np.array([bed_lo[0], y, bz]), np.array([bed_hi[0], y, bz])))
            draw_lines([(to_px(a @ R.T), to_px(b @ R.T)) for a, b in grid], GRID_RGB, img, zbuf, 0.05)

    normals_v = mesh.face_normals @ R.T
    front = normals_v[:, 2] > 1e-6
    light = np.array([-0.35, 0.45, 0.82])
    light /= np.linalg.norm(light)
    lum = 0.30 + 0.70 * np.clip(normals_v[front] @ light, 0, 1)
    colors = np.clip(lum[:, None] * PART_RGB[None, :] + 0.06, 0, 1)
    tris_px = to_px(verts[mesh.faces[front]])
    rasterize(tris_px, colors, img, zbuf)

    try:
        angles = mesh.face_adjacency_angles
        edges = mesh.face_adjacency_edges[angles > math.radians(25)]
        segs = [(to_px(verts[a]), to_px(verts[b])) for a, b in edges]
        draw_lines(segs, EDGE_RGB, img, zbuf, eps=0.08)
    except Exception:
        pass
    return img, R


def render(job: Path) -> list[Path]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import trimesh

    mesh = trimesh.load(job / "part.stl", force="mesh")
    size = mesh.bounds[1] - mesh.bounds[0]
    out_dir = job / "renders"
    out_dir.mkdir(exist_ok=True)
    written = []
    for name, (elev, azim) in VIEWS.items():
        img, R = render_view(mesh, elev, azim, with_bed=(name != "bottom"))
        fig = plt.figure(figsize=(8, 8.4), dpi=100)
        ax = fig.add_axes([0, 0, 1, 0.95])
        ax.imshow(img, interpolation="antialiased")
        ax.set_axis_off()
        origin = np.array([70, SIZE - 70])
        for vec, label, col in ((np.array([1, 0, 0]), "X", "#c0392b"), (np.array([0, 1, 0]), "Y", "#27ae60"),
                                (np.array([0, 0, 1]), "Z", "#2e6fbf")):
            v = R[:2] @ vec
            if np.hypot(*v) < 0.05:
                ax.text(*origin, label + "·", color=col, fontsize=11, ha="center", va="center", weight="bold")
                continue
            tip = origin + np.array([v[0], -v[1]]) * 45
            ax.annotate("", xy=tip, xytext=origin, arrowprops=dict(arrowstyle="->", color=col, lw=2))
            ax.text(*(origin + np.array([v[0], -v[1]]) * 58), label, color=col, fontsize=11,
                    ha="center", va="center", weight="bold")
        fig.suptitle(f"{job.name} · {name} · {size[0]:.1f} × {size[1]:.1f} × {size[2]:.1f} mm"
                     + ("" if name == "bottom" else " · bed grid 10 mm"), fontsize=12, y=0.985)
        path = out_dir / f"{name}.png"
        fig.savefig(path)
        plt.close(fig)
        written.append(path)
    return written


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Render review PNGs of jobs/<id>/part.stl.")
    ap.add_argument("job")
    args = ap.parse_args(argv)
    job = Path(args.job).resolve()
    if not (job / "part.stl").exists():
        print(f"No part.stl in {job}; run tools/cad_build.py first.", file=sys.stderr)
        return 2
    for p in render(job):
        print(p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
