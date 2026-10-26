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
from build123d import Align, Box, Pos, Vector  # noqa: E402
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
zf_ = ns["FRONT_SCREWS"][0][1]
check("front M2.5 holes Ø3.0 (teardrop +y) at y +-24, z 2.5 (round 7: 3 -> 2.5, FRONT_SCREWS); the Ø6 washer's seat "
      "(r 3) whole on the front face; 1.75 to slot B's lower edge (z 5.75)",
      abs(zf_ - 2.5) < 1e-9 and all(not solid(37, y, 2.5) and not solid(37, y, 1.05) and solid(37, y, 0.95)
                                    and not solid(37, y - 1.45, 2.5) and solid(37, y - 1.55, 2.5)
                                    and not solid(37, y + 2.05, 2.5) and solid(37, y + 2.2, 2.5)
                                    and all(solid(39.8, y + dy, 2.5 + dz) for dy, dz in ((2.95, 0), (-2.95, 0), (0, 2.95),
                                                                                         (0, -2.95), (2.1, 2.1),
                                                                                         (-2.1, -2.1)))
                                    and solid(37, y, 5.7) for y in (-24.0, 24.0)),
      f"z {zf_}")
ce = ns["SLOT_EDGE_CHAMFER"]
check("0.3 x 45° chamfer on the front edge of slot A's lower side (z 38.25) and slot B's upper side (z 16.25) (round 7)",
      abs(ce - 0.3) < 1e-9
      and all(not solid(39.8, y, 38.2) and solid(39.45, y, 38.2) and solid(39.8, y, 37.9) for y in (-31.5, -25.0, -10.0))
      and all(not solid(39.8, y, 16.3) and solid(39.45, y, 16.3) and solid(39.8, y, 16.6) for y in (10.0, 25.0, 31.5)),
      "probed at x 39.8 / 39.45, 0.05 into the slot side, and 0.35 off it on the front face")
check("pass-through r 11.4 on the pinion axis (y 0, z 27.25)", not solid(37, -8.0, 19.25) and solid(37, -8.2, 19.05)
      and not solid(37, 11.2, 27.25))
check("first tie: post x 14.35..22.35 + web, y -32..-24, |z - 27.25| <= 8", solid(14.5, -28, 30) and solid(30, -28, 27)
      and not solid(30, -28, 35.4) and not solid(30, -23.8, 27))
check("second tie: 8 mm post x 14.35..22.35 (claw strength round 3: 4 -> 8) + web, full at y 24..32",
      solid(14.4, 25, 20) and not solid(14.3, 25, 20) and solid(22.3, 25, 20) and solid(16, 31.9, 30)
      and solid(30, 24.1, 19.4) and solid(30, 24.1, 35.1) and not solid(30, 28, 35.4) and not solid(30, 28, 19.1))
check("second tie's post foot flats z 18.05 over y 24..32: FOOT_CLR 0.30 over the rail block's CAD top 17.75 (round 6; "
      "round 5 17.85)", abs(ns["TIE2_FOOT_Z"] - 18.05) < 1e-9 and abs(ns["FOOT_CLR"] - 0.30) < 1e-9
      and all(solid(x, y, 18.1) and not solid(x, y, 18.0) for x in (16.45, 21.0, 22.3) for y in (24.1, 26.0, 31.9)),
      "probes x 16.45 (between the ridge and the anchor hole) / 21.0 / 22.3, y 24.1-31.9")
check("post's 45° underside: from the foot at y 24 to the lip at y 5.3",
      solid(16, 15, 27.15) and not solid(16, 15, 26.95) and solid(16, 5.9, 36.25) and not solid(16, 5.9, 36.05)
      and solid(16, 5.4, 36.8) and not solid(16, 5.1, 36.7), "z = 18.05 + (24 - y)")
zt, za, xc, zf = ns["RIDGE_TIP_Z"], ns["RIDGE_APEX_Z"], ns["VSEAT_XC"], ns["TIE2_FOOT_Z"]
check("V-ridge under the foot (round 6): the groove's own 90° V (VSEAT_CLR 0), virtual apex z 16.95 on x 15.25, flanks "
      "up to the flats (base x 14.15..16.35 at z 18.05, 2.2 wide), tip cut flat at z 17.35 (0.8 wide), full from y 24.7 "
      "to 32, 45° lead-in from y 24",
      abs(za - 16.95) < 1e-9 and abs(zt - 17.35) < 1e-9 and abs(xc - 15.25) < 1e-9
      and all(solid(xc + s * (z - za - 0.05), y, z) and not solid(xc + s * (z - za + 0.05), y, z)
              for s in (-1, 1) for z in (17.4, 17.7, 18.0) for y in (24.9, 28.0, 31.9))
      and solid(xc, 28, 17.4) and not solid(xc, 28, 17.3) and solid(xc + 0.35, 28, 17.4) and solid(xc - 0.35, 28, 17.4)
      and not solid(xc, 32.1, 17.5)
      and solid(xc, 24.5, 17.6) and not solid(xc, 24.4, 17.6) and solid(xc, 24.7, 17.4) and not solid(xc, 24.6, 17.4)
      and not solid(xc, 23.9, 18.0), "flanks probed ±0.05 at z 17.4 / 17.7 / 18.0, y 24.9 / 28 / 31.9; lead-in y + z >= 42.05")
x_b0, x_b1 = xc - (zf - za), xc + (zf - za)
ax, ay = ns["ANCHOR_XY"]
r_hole = (ns["M3_CLEAR"] + ns["HOLE_COMP"]) / 2
check("ridge's -x base 0.2 behind the post's back face (x 14.35), a bump on the post's face in print",
      abs((ns["LIP_X0"] - x_b0) - 0.2) < 1e-9 and solid(x_b0 + 0.05, 28, zf - 0.01) and not solid(x_b0 - 0.05, 28, zf - 0.01)
      and not solid(ns["LIP_X0"] - 0.05, 28, zf + 0.05), f"base x {x_b0:.2f}..{x_b1:.2f}; post's back face x {ns['LIP_X0']:.2f}")
check("ridge's +x base 0.2 from the anchor hole's edge on the flats plane",
      abs((ax - r_hole) - x_b1 - 0.2) < 1e-9 and solid(x_b1 - 0.05, ay, zf - 0.01) and not solid(x_b1 + 0.05, ay, zf - 0.01)
      and not solid(ax - r_hole + 0.05, ay, zf + 0.1) and solid(ax - r_hole - 0.05, ay, zf + 0.1),
      f"ridge {x_b1:.2f}, hole edge {ax - r_hole:.2f}")
fr = runpy.run_path(str(JOB.parent / "20261026-arm-claw-frame" / "model.py"), run_name="model")["design"]()
ov = d & fr
ov_v = sum(s.volume for s in ov.solids()) if ov else 0.0
seat = Pos(13.5, 22.5, 16.5) * Box(4, 10.5, 2, align=(Align.MIN,) * 3)     # x 13.5..17.5, y 22.5..33, z 16.5..18.5
gap_fl = (d & seat).distance_to(fr & seat)
flats = Pos(16.6, 24.5, 17.0) * Box(5.7, 7.4, 1.5, align=(Align.MIN,) * 3)  # beside the ridge: the flats over the block
gap_ft = (d & flats).distance_to(fr & flats)
topw = Pos(3.5, -32, 47.0) * Box(6.5, 64, 3, align=(Align.MIN,) * 3)       # the top wall over the bulkhead (x 3.5..10)
gap_tw = (d & topw).distance_to(fr & topw)
z_slot = 17.2                                   # top of the groove's first layer (17.0..17.2), which prints closed
check("CAD, cover seated at nominal: the ridge's flanks touch the groove's (0 mm³, distance 0) before anything else: the "
      "foot's flats 0.30 over the block, the tip 0.15 over the groove's closed first layer, the top wall 0.05 over the "
      "bulkhead", ov_v < 1e-6 and gap_fl < 1e-6 and abs(gap_ft - 0.30) < 1e-6 and abs(zt - z_slot - 0.15) < 1e-9
      and abs(gap_tw - 0.05) < 1e-6,
      f"overlap {ov_v:.4f} mm3, flanks {gap_fl:.4f}, flats {gap_ft:.4f}, tip over 17.2 {zt - z_slot:.3f}, top wall {gap_tw:.4f}")
# As printed (round 6 scratch slice of both part.stl files with the arm's command, G-code read back; design_review.md):
# frame bulkhead top 48.4, rail block top 17.8, groove walls at half-widths 0.15 / 0.35 / 0.55 / 0.75 in the layers
# ending 17.2 / 17.4 / 17.6 / 17.8 (each layer's top corner 0.1 inside the CAD flank); the cover's ridge, tip and flats
# print to CAD (external perimeters 0.225 inside them). A corner bead rounding r (0.075 nominal) moves the 45° ridge's
# contact (2 - sqrt 2) r further out. Lowered onto the printed frame, the ridge lands on those corners and sits `lift` above
# its CAD seat:
Z_BULK_PR, Z_BLOCK_PR, INSET, R_BEAD = 48.4, 17.8, 0.1, 0.075
lift = INSET - (2 - 2 ** 0.5) * R_BEAD
top_pr = ns["Z_TOP0"] + lift - Z_BULK_PR
flat_pr = zf + lift - Z_BLOCK_PR
tip_pr = zt + lift - z_slot
check("as printed, nominal: the ridge lands on the groove's layer corners first; before the screws the top wall stands "
      "~0.16 over the printed bulkhead (BUILD_GUIDE §4 step 9: a 0.03 feeler must go in), the flats ~0.3 over the block, "
      "the tip ~0.2 over the closed first layer", 0.10 <= top_pr <= 0.20 and flat_pr >= 0.25 and tip_pr >= 0.15,
      f"lift {lift:.3f}: top wall {top_pr:.3f}, flats {flat_pr:.3f}, tip {tip_pr:.3f}")
anc = [h for h in holes if abs(h["diameter"] - 3.6) < 0.01 and abs(h["point_on_axis"][0] - ax) < 0.01
       and abs(h["point_on_axis"][2] - (ay + 32)) < 0.01]
check("anchor hole Ø3.4 + HOLE_COMP = Ø3.6 at (18.35, 28), vertical through the top wall, lip and post z 18.05..51.5 "
      "(teardrop +y)",
      len(anc) == 1 and all(not solid(ax, ay, z) for z in (18.1, 25, 36, 40, 49, 51.4))
      and not solid(16.6, ay, 25) and solid(16.5, ay, 25)
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
