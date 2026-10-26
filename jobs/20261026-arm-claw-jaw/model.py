"""Claw jaw (x2, identical): rack + neck + finger in one piece. Printed standing on the rack's
back end (claw x = X_P0 face on the bed), so the rack teeth are drawn in the bed plane and the
finger grows upwards.

Design frame = claw frame G (../20261025-robot-arm-assembly/claw_frame.py), drawn as JAW A in
the CLOSED pose: the rack above the pinion with its teeth pointing down (-z), the neck through
the cover's slot A, the finger on the -y side with its grip face on y = 0. Jaw B is the same
part turned 180° about the pinion axis (the claw x axis through y 0, z ZS).

Round 2 (claw DFM + strength round 1, deep review 03 SYS-08):
- rack 4 mm taller behind the roots (RACK_BACK 10) and 2 teeth longer at -y, so the 20 x 10
  neck sits on solid rack with no tooth gaps under it; rack and pinion face 10; root fillets
  r 0.3 (tools/gears.py); tips topped 0.15; teeth 0.25 thinner at the pitch line (0.35 per mesh
  with the pinion's 0.10);
- neck root fillets r 4 at its two y edges; finger 12 thick to TAPER_X0, 6 by TAPER_X1;
  full-height 45° gusset from the neck into the finger; r 3 at the re-entrant kinks;
- finger top flat at the neck top to TOP_KINK_X, then 45° down to the grip zone (lighter, and
  the camera sees the fingertips over it);
- 0.3 mm chamfer on every bed edge (tooth outline included); 2 mm chamfer on the rack's
  back/front edge beside the cover's corner fillet.
Grip face: 0.6 mm V-grooves across the finger and a 1.5 mm V-notch along its centre line.
"""
import math
import sys
from pathlib import Path

from build123d import BuildPart, BuildSketch, Location, Plane, Polygon, Rot, extrude
from cadlib import to_bed

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "20261025-robot-arm-assembly"))
from claw_frame import (BLADE_T, BLADE_T_ROOT, FACE_W, GRIP_HALF, GRIP_X0, KINK_FILLET, M,  # noqa: E402
                        NECK_FILLET, NECK_X1, NECK_Y, NECK_Z, P_CIRC, R_P, RACK_BACK, RACK_BACKLASH, RACK_EDGE_CHAMFER,
                        RACK_EDGE_Y0, RACK_OUT, RACK_ROOT_FILLET, RACK_Y, TAPER_X0, TAPER_X1, TIP_RELIEF,
                        TOP_KINK_X, X_P1, X_TIP, ZS)

from gears import rack_bar  # noqa: E402

# --- parameters (mm) -----------------------------------------------------------
BED_CHAMFER = 0.3          # DFM fix 1: every edge of the bed face (rack back end, tooth outline included)
TIP_CHAMFER = 4.0          # 45° corners at the fingertip (x-z outline)
TIP_BEVEL = 3.5            # outer-face bevel at the fingertip (thin tip for small parts)
GROOVE_D, GROOVE_PITCH = 0.6, 2.0
GROOVE_X = (GRIP_X0 + 1.0, X_TIP - TIP_CHAMFER - 1.5)   # stop short of the tip chamfers (no slivers)
NOTCH_D = 1.5
GUSSET = NECK_Y - BLADE_T_ROOT   # 8: 45° flare in plan from the 20 mm neck into the 12 mm finger
TAPER_FILLET = 3.0         # fillet where the taper meets the 6 mm tip section
# rack frame in G: rack_bar's X (teeth row) along +y, its tooth direction (+Y) along -z,
# its extrusion (+Z) along -x; pitch line on z = ZS + R_P. A tooth GAP sits over the pinion
# axis (y 0) in the closed pose, facing the pinion's tooth 0.
RACK_LOC = Location(Plane(origin=(X_P1, 0, ZS + R_P), x_dir=(0, 1, 0), z_dir=(-1, 0, 0)))


def _prism_xz(pts, y0, y1):
    """Polygon in the x-z plane, extruded from y0 to y1."""
    with BuildPart() as bp:
        with BuildSketch(Plane.XZ.offset(-y1)):        # Plane.XZ's normal is -y: the sketch sits on
            Polygon(*pts, align=None)                  # y = y1 and extrudes towards -y, down to y0
        extrude(amount=y1 - y0)
    return bp.part


def _prism_xy(pts, z0, z1):
    with BuildPart() as bp:
        with BuildSketch(Plane.XY.offset(z0)):
            Polygon(*pts, align=None)
        extrude(amount=z1 - z0)
    return bp.part


def _prism_yz(pts, x0, x1):
    with BuildPart() as bp:
        with BuildSketch(Plane.YZ.offset(x0)):
            Polygon(*pts, align=None)
        extrude(amount=x1 - x0)
    return bp.part


def _round(pts, corners, r, n=8):
    """Replace each corner index in `corners` of the closed polyline `pts` by an arc of radius r
    tangent to both neighbouring edges (an inside fillet at a re-entrant corner)."""
    out = []
    for i, p in enumerate(pts):
        if i not in corners:
            out.append(p)
            continue
        a, c = pts[i - 1], pts[(i + 1) % len(pts)]
        u = ((a[0] - p[0]), (a[1] - p[1])); lu = math.hypot(*u); u = (u[0] / lu, u[1] / lu)
        v = ((c[0] - p[0]), (c[1] - p[1])); lv = math.hypot(*v); v = (v[0] / lv, v[1] / lv)
        half = math.acos(max(-1.0, min(1.0, u[0] * v[0] + u[1] * v[1]))) / 2
        t = r / math.tan(half)                       # tangent length from the corner
        bis = (u[0] + v[0], u[1] + v[1]); lb = math.hypot(*bis); bis = (bis[0] / lb, bis[1] / lb)
        cen = (p[0] + bis[0] * r / math.sin(half), p[1] + bis[1] * r / math.sin(half))
        t0 = (p[0] + u[0] * t, p[1] + u[1] * t)
        t1 = (p[0] + v[0] * t, p[1] + v[1] * t)
        a0 = math.atan2(t0[1] - cen[1], t0[0] - cen[0])
        a1 = math.atan2(t1[1] - cen[1], t1[0] - cen[0])
        da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
        out += [(cen[0] + r * math.cos(a0 + da * k / n), cen[1] + r * math.sin(a0 + da * k / n)) for k in range(n + 1)]
    return out


def side_outline():
    """Neck + finger silhouette in the x-z plane (jaw A)."""
    z_n0, z_n1 = ZS + NECK_Z[0], ZS + NECK_Z[1]
    z_lo, z_hi = ZS - GRIP_HALF, ZS + GRIP_HALF
    x0 = X_P1 - 0.01
    pts = [(x0, z_n0), (NECK_X1, z_n0),                                  # 1: re-entrant (neck -> 45° lower edge)
           (NECK_X1 + (z_n0 - z_lo), z_lo), (X_TIP - TIP_CHAMFER, z_lo), (X_TIP, z_lo + TIP_CHAMFER),
           (X_TIP, z_hi - TIP_CHAMFER), (X_TIP - TIP_CHAMFER, z_hi),
           (TOP_KINK_X + (z_n1 - z_hi), z_hi),                            # 7: re-entrant (45° top -> grip-zone top)
           (TOP_KINK_X, z_n1), (x0, z_n1)]
    return _round(pts, {1, 7}, KINK_FILLET)


def plan_outline():
    """Neck + gusset + finger in plan (x-y), jaw A: grip face on y = 0, outer face at -y."""
    x0 = X_P1 - 0.01
    pts = [(x0, 0.0), (X_TIP + 1.0, 0.0), (X_TIP + 1.0, -BLADE_T), (TAPER_X1, -BLADE_T),   # 3: re-entrant
           (TAPER_X0, -BLADE_T_ROOT), (NECK_X1 + GUSSET, -BLADE_T_ROOT),                  # 5: re-entrant (gusset end)
           (NECK_X1, -NECK_Y), (x0, -NECK_Y)]
    pts = _round(pts, {5}, KINK_FILLET)
    return _round(pts, {3}, TAPER_FILLET)


def _neck_root_fillet(y_edge, sign):
    """Inside fillet between the rack's front face (x = X_P1) and a neck side face (y = y_edge);
    sign +1 puts it on the +y side of the edge."""
    r = NECK_FILLET
    arc = [(X_P1 + r - r * math.cos(t), y_edge + sign * (r - r * math.sin(t)))
           for t in [k * (math.pi / 2) / 12 for k in range(13)]]   # from (X_P1, y+r) to (X_P1+r, y)
    pts = [(X_P1 - 0.01, y_edge)] + [(arc[0][0] - 0.01, arc[0][1])] + arc[1:]
    return _prism_xy(pts, ZS + NECK_Z[0], ZS + NECK_Z[1])


def rack():
    # rack_bar's z = FACE_W end is the bed face (claw x = X_P0): 45° chamfer there, tooth outline included
    r = rack_bar(M, RACK_Y[0], RACK_Y[1], FACE_W, RACK_BACK, backlash=RACK_BACKLASH, phase=P_CIRC / 2,
                 root_fillet=RACK_ROOT_FILLET, tip_relief=TIP_RELIEF, chamfer=(0.0, BED_CHAMFER))
    return RACK_LOC * r


def design():
    j = rack()
    body = _prism_xy(plan_outline(), ZS - GRIP_HALF - 1, ZS + NECK_Z[1] + 1) & \
        _prism_xz(side_outline(), -NECK_Y - 1, 1.0)
    j += body
    j += _neck_root_fillet(0.0, +1) + _neck_root_fillet(-NECK_Y, -1)
    # 45° chamfer on the rack's back/front edge, beyond the neck (clears the cover's corner fillet)
    c, zb = RACK_EDGE_CHAMFER, ZS + RACK_OUT
    tri = _prism_xz([(X_P1 + 0.01, zb + 0.01), (X_P1 - c - 0.01, zb + 0.01), (X_P1 + 0.01, zb - c - 0.01)],
                    RACK_EDGE_Y0, RACK_Y[1] + 1)
    j -= tri
    # grip face: V-grooves across the finger (along z) ...
    x = GROOVE_X[0]
    while x <= GROOVE_X[1]:
        j -= _prism_xy([(x - GROOVE_D, 0.01), (x, -GROOVE_D), (x + GROOVE_D, 0.01)],
                       ZS - GRIP_HALF - 1, ZS + GRIP_HALF + 1)
        x += GROOVE_PITCH
    # ... and a V-notch along it, on the claw's centre line
    j -= _prism_yz([(0.01, ZS - NOTCH_D), (-NOTCH_D, ZS), (0.01, ZS + NOTCH_D)], GRIP_X0 - 4, X_TIP + 1)
    # thin fingertip: bevel the outer face
    j -= _prism_xy([(X_TIP - TIP_BEVEL * 2 - 2, -BLADE_T - 1), (X_TIP + 1, -BLADE_T - 1),
                    (X_TIP + 1, -BLADE_T + TIP_BEVEL + 0.5)], ZS - GRIP_HALF - 1, ZS + GRIP_HALF + 1)
    return j


def build():
    return to_bed(Rot(0, -90, 0) * design())      # claw +x up: rack back end on the bed
