"""Idler (×2): the drive sprocket's geometry with a round running bore, free on an M3 bolt
held in the chassis's tension slot. Toothed so the track wraps it exactly like the sprocket
(a smooth idler would stretch the polygonal wrap). Printed outer face down, hub up.
Round 3: the sprocket now bolts to a metal hub; this part keeps the round-bore branch of the
shared model (Ø10 hub from the wall washer to the disc, Ø3.5 printed bore), so only the shared
tooth-root chamfer change (it now starts on the disc circle) reaches it.
Round 5 (chassis strength round 4's fix, approved by the user): the chassis's steel nut plate, a Ø9
washer and the wall nut now sit outside the wall (|y| 38-43.2), so the hub starts at |y| 43.7
(rover_frame.IDLER_HUB_Y0; the shared model's HUB_Z0_ROUND = -11.3), 5.2 mm shorter: the part is
14.8 mm tall instead of 20. The disc, teeth, track plane, bore and bolt stack beyond the disc don't move.
"""
import runpy
from pathlib import Path

_sp = runpy.run_path(str(Path(__file__).resolve().parent.parent / "20261026-rover-sprocket" / "model.py"),
                     init_globals={"__file__": str(Path(__file__).resolve().parent.parent
                                                   / "20261026-rover-sprocket" / "model.py")},
                     run_name="sprocket")

# --- parameters (mm) -----------------------------------------------------------
ROUND_BORE = 3.5      # printed running bore on the M3 bolt, 0.5 mm running clearance (DFM round 1)


def design():
    g = _sp["design"].__globals__
    old = g["BORE"], g["ROUND_BORE"]
    g["BORE"], g["ROUND_BORE"] = "round", ROUND_BORE
    try:
        return _sp["design"]()
    finally:
        g["BORE"], g["ROUND_BORE"] = old


def build():
    from build123d import Rot
    from cadlib import to_bed
    return to_bed(Rot(180, 0, 0) * design())
