# Design brief: Idler (×2)

Job: 20261026-rover-idler · design-lead (round 3) · 2026-10-26

## Material
PETG for every rover part: tough against knocks, wears acceptably on steel pins, prints on an open-frame MK3S, softening point ~70 °C, well above the 40 °C service. No library data yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Outer disc face on the bed, hub up. Bearing on the bore is in the layer plane. The bore runs the full 20 mm on the bolt, so the hub doesn't act as a cantilever.

## Concept
The sprocket's toothed geometry with a round Ø3.5 running bore and a Ø10 hub, free on its M3 × 40 bolt in the chassis's tension slot, so the track wraps it exactly like the sprocket. It runs the sprocket's model.py with BORE = "round". The round-3 sprocket changes (metal hub, slots, no spacer) stay inside the sprocket's own branch. The only shared change that reaches the idler is the tooth-root chamfer, which now starts on the disc circle (DFM round 2, R1).

**Round 3, idler mounting (chassis job):**
- **Positive stop:** an M3 × 20 set screw along +X bears on the bolt head and holds the idler forward without friction, against 29.8 N at a reverse stall. It also sets the track tension.
- **Head washer:** a Ø9 DIN 9021 washer under the head.
- **Bolt:** M3 × 40, class 12.9, fully threaded (BOSS_IN 5.5 moved the head to |y| 27.2).

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Running bore | Ø3.5 printed (Ø3.7 CAD) | +0.15/−0 | running fit on M3, 0.5 clearance | HOLE_COMP +0.2 | default from fdm-design-rules (no library row) |
| Pitch radius | 16.18 | ±0.15 | matches the 10 mm link pitch | — | rover_frame.RP |

Printed targets for the whole rover: see the chassis brief. `print_requirements.json` now asks for `elefant_foot_compensation` 0.2, so the bore's first layer doesn't narrow (DFM round 2, R1).

## Parameters exposed by model.py
ROUND_BORE (+ the sprocket model's parameters). `cad_checks.py` proves them on the geometry.

## Risks
- **Bore wear on the bolt threads:** class 12.9 bolts, and a 0.5 mm running clearance.
- **Idler creeping back under the track pull:** the jack screw holds it, and the pen mark in proof test 1 confirms it.
