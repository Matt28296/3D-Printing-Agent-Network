"""jobs/20261026-arm-claw-cover/cad_checks.py: prove the critical dimensions on the built geometry.

Run from the project root: python3 jobs/20261026-arm-claw-cover/cad_checks.py
Exit code 0 = every check passed. Probes use design() (the cover as fitted, claw frame G) and design() + supports()
(as printed, before the two pillars are snapped off); build() is the printed part standing on its -y end.
"""
import runpy
import sys
from pathlib import Path

JOB = Path(__file__).resolve().parent
sys.path.insert(0, str(JOB.parents[1] / "tools"))
from build123d import Vector  # noqa: E402
from cadlib import bbox, measure_holes  # noqa: E402

ns = runpy.run_path(str(JOB / "model.py"), run_name="model")
part = ns["build"]()
d = ns["design"]()
sup = ns["supports"]()
printed = d + sup
size = bbox(part)["size"]
holes = measure_holes(part)
failures = []


def check(name, ok, detail=""):
    print(f"{'PASS' if ok else 'FAIL'}  {name}: {detail}")
    if not ok:
        failures.append(name)


def solid(x, y, z, s=None):
    return (d if s is None else s).is_inside(Vector(x, y, z))


# ---- CHECKS: one line per critical dimension in design_brief.md -----------------
check("printed size 39.85 x 57.5 x 64 (G x, z -6..51.5, y +-32)", all(abs(a - b) < 0.01 for a, b in zip(size, [39.85, 57.5, 64.0])),
      size)
check("one solid as printed, one as fitted", len(part.solids()) == 1 and len(d.solids()) == 1, (len(part.solids()), len(d.solids())))
dia = sorted(round(h["diameter"], 2) for h in holes)
check("holes: 2 x M2.5 Ø3.0, 3 x M3 Ø3.6 (2 top + the anchor), pass-through Ø22.8", dia == [3.0, 3.0, 3.6, 3.6, 3.6, 22.8],
      dia)
check("front plate x 34.85..39.85, down to z -6", solid(34.9, -20, 0) and solid(39.8, -20, 0) and not solid(34.8, -20, 0)
      and solid(37, -20, -5.9) and not solid(37, -20, -6.1))
check("top wall underside z 48.5, top z 51.5, from x 0", solid(0.1, -20, 50) and not solid(10, -20, 48.4) and solid(10, -20, 48.6)
      and not solid(10, -20, 51.6))
check("lip x 14.35..22.35 (GUIDE_T 8), z 36.75..48.5", solid(14.4, 0, 45) and not solid(14.3, 0, 45) and solid(22.3, 0, 37)
      and not solid(22.4, 0, 40) and not solid(18, 0, 36.6))
check("slot A z 38.25..48.5, open at -y", not solid(37, -20, 43) and not solid(37, -31.9, 38.3) and solid(37, -20, 38.1))
check("slot B z 5.75..16.25, open at +y", not solid(37, 20, 11) and solid(37, 20, 5.6) and solid(37, 20, 16.4)
      and not solid(37, 31.9, 6.0))
check("pass-through r 11.4 on the pinion axis (y 0, z 27.25)", not solid(37, -8.0, 19.25) and solid(37, -8.2, 19.05)
      and not solid(37, 11.2, 27.25))
check("first tie: post x 14.35..22.35 + web, y -32..-24, |z - 27.25| <= 8", solid(14.5, -28, 30) and solid(30, -28, 27)
      and not solid(30, -28, 35.4) and not solid(30, -23.8, 27))
check("second tie: 8 mm post x 14.35..22.35 (claw strength round 3: 4 -> 8) + web, full at y 24..32",
      solid(14.4, 25, 20) and not solid(14.3, 25, 20) and solid(22.3, 25, 20) and solid(16, 31.9, 30)
      and solid(30, 24.1, 19.4) and solid(30, 24.1, 35.1) and not solid(30, 28, 35.4) and not solid(30, 28, 19.1))
check("second tie's post stands on the rail block: foot z 17.75 over y 24..32 (was 19.25)",
      all(solid(x, y, 17.8) and not solid(x, y, 17.7) for x in (14.4, 16.0, 22.3) for y in (24.1, 26.0, 31.9)),
      "probes x 14.4-22.3, y 24.1-31.9")
check("post's 45° underside: from the foot at y 24 to the lip at y 5 (2.5 over the claw servo's case at y 5.9)",
      solid(16, 15, 26.85) and not solid(16, 15, 26.65) and solid(16, 5.9, 35.95) and not solid(16, 5.9, 35.75)
      and solid(16, 5.1, 36.8) and not solid(16, 4.9, 36.7), "z = 17.75 + (24 - y)")
ax, ay = ns["ANCHOR_XY"]
anc = [h for h in holes if abs(h["diameter"] - 3.6) < 0.01 and abs(h["point_on_axis"][0] - ax) < 0.01
       and abs(h["point_on_axis"][2] - (ay + 32)) < 0.01]
check("anchor hole Ø3.4 + HOLE_COMP = Ø3.6 at (18.35, 28), vertical through the top wall, lip and post (teardrop +y)",
      len(anc) == 1 and all(not solid(ax, ay, z) for z in (17.8, 25, 36, 40, 49, 51.4))
      and not solid(ax, ay + 2.4, 30) and solid(ax, ay + 2.7, 30) and not solid(ax + 1.75, ay, 30) and solid(ax + 1.85, ay, 30)
      and not solid(ax, ay - 1.75, 30) and solid(ax, ay - 1.85, 30), f"{[h['arc_deg'] for h in anc]}")
check("walls round the anchor hole: 2.2 to the post's faces, 1.45 at the teardrop's tip to y 32",
      solid(14.4, ay, 30) and solid(ax - 1.85, ay, 30) and solid(22.3, ay, 30) and solid(ax, 31.9, 30) and solid(ax, 30.6, 30))
check("second tie: 45° undersides (web empty at y 12, z 27; post from the lip at y 5 since round 4)", not solid(30, 12, 27)
      and solid(30, 22, 27) and solid(20, 6.8, 36.6) and not solid(20, 6.8, 30) and not solid(20, 10, 19.5))
check("second tie clear of the pinion (r 11.4) behind the plate", not solid(23, 8.0, 35.2) and not solid(33, 0, 38.0))
check("support pillars only as printed: under the piece beside slot A (y -7..6.25, z 36.8..38.1) and beside slot B "
      "(y -8..6.75, z 16.45..18.05, 1.6 thick: claw DFM round 3 fix 1)", solid(37, 0, 37.45, printed) and not solid(37, 0, 37.45)
      and solid(37, 0, 17.25, printed) and not solid(37, 0, 17.25) and len(sup.solids()) == 2
      and not solid(37, 6.4, 37.45, printed) and solid(37, 6.6, 37.45) and not solid(37, 6.9, 17.25, printed)
      and solid(37, 7.1, 17.25))
sb = ns["SUP_B"]
check("pillar B: G y -8 -> 6.75, z 16.45..18.05, x 35.35..39.35, its foot inside the plate at y -8",
      abs(sb[0] + 8.0) < 1e-9 and abs(sb[2] - 16.45) < 1e-9 and abs(sb[3] - 18.05) < 1e-9
      and all(solid(x, 0, z, printed) for x in (35.4, 39.3) for z in (16.5, 18.0))
      and not solid(37, 0, 16.4, printed) and not solid(37, 0, 18.1, printed)
      and not solid(35.3, 0, 17.25, printed) and not solid(39.4, 0, 17.25, printed)
      and solid(37, -7.9, 16.5) and solid(37, -7.9, 18.0) and not solid(37, -8.1, 18.0, sup)
      and solid(37, 6.7, 17.25, printed) and not solid(37, 6.8, 17.25, printed),
      f"SUP_B {sb}")
check("pillar B carries piece (b)'s first layer (G y 7.0..7.2, z 16.25..18.33) within 0.3 in z",
      solid(37, 7.1, 16.3) and solid(37, 7.1, 18.3) and not solid(37, 7.1, 16.2) and not solid(37, 7.1, 18.36)
      and 16.45 - 16.25 <= 0.3 and 18.33 - 18.05 <= 0.3, "overhang 0.20 below / 0.28 above the pillar")
# ---------------------------------------------------------------------------------

sys.exit(1 if failures else 0)
