"""Idler (×2): the drive sprocket's geometry with a round running bore, free on an M3 bolt
held in the chassis's tension slot. Toothed so the track wraps it exactly like the sprocket
(a smooth idler would stretch the polygonal wrap). Printed outer face down, hub up.
Round 3: the sprocket now bolts to a metal hub; this part keeps the round-bore branch of the
shared model (Ø10 hub from the wall washer to the disc, Ø3.5 printed bore), so only the shared
tooth-root chamfer change (it now starts on the disc circle) reaches it.
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
