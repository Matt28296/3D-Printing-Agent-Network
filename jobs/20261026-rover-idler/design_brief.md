# Design brief: Idler (×2)

Job: 20261026-rover-idler · design-lead (round 3; round 5: the chassis's round-5 clamp fix shortens the hub, approved by the user) · 2026-10-26

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

**Round 5, hub 5.2 mm shorter (chassis strength round 4's fix, approved by the user):**
- **Why.** The chassis's round-4 nut slot left a 3.4 mm PETG web that failed (SF 0.61). The fix moves the steel nut plate onto the wall's outer face, with a Ø9 washer under the wall nut. That stack takes |y| 38–43.2 outside the wall. With the running washer (43.2–43.7) the hub now starts at **|y| 43.7** instead of 38.5 (`rover_frame.IDLER_HUB_Y0`; the shared model's `HUB_Z0_ROUND` −16.5 → −11.3).
- **What changes.** The part is 14.8 mm tall instead of 20 (hub 7.8 instead of 13); volume 4 853 → 4 501 mm³.
- **What doesn't move:** the disc and teeth (track plane |y| 55, ±3.5), the bore size, the outer running washer, the nyloc and the bolt.
- **Its own fits after the change** (assembly_check.json, round 5):
  - **Bore on the bolt.** Still Ø3.5 printed on the fully threaded M3 (0.5 diametral clearance, a free-running fit), now 14.8 long (L/D 4.9 on Ø3; it was 6.7).
    - The clearance lets the idler cock about 1.9° on the bolt (1.4° before). About 0.3 mm of end play on the Ø7 washers would allow 2.5°, so the bore sets the limit.
    - At the tooth tips (r 17.9) that is about 0.6 mm sideways, against the link notch's 0.5 mm a side (0.45 mm before). The track's links straighten the idler as the teeth enter, as they already did.
    - Bearing: strength round 3 took the effective bearing length as the 7 mm disc plus a 45° spread into the hub (5.08 mm). The hub is still longer than that spread, so the bore rows I1–I4 should not change. The strength review re-checks them.
  - **Running washers.** The inner ISO 7089 washer now sits on the wall nut's outer face (43.2–43.7), not on the wall. The hub's Ø10 end face bears on it over r 1.85–3.5, as before on the wall washer. The outer washer (58.5–59.0) is unchanged.
  - **Nyloc and thread.** The nyloc stays at 59.0–63.0 and the bolt tip at 67.2: **4.2 mm of thread past the nyloc** (≥ 1.5 required). The fully threaded M3 × 40 engages the wall nut at 40.8–43.2; a partly threaded ISO 4762 screw would not reach it.
  - **Clearances.** The hub (r 5), nut and washers (r ≤ 4.5) stay inside the links' wrap (r ≥ 12.39). The idler and its hardware clear the chassis and jack screw at both slot ends, and 7 teeth mesh.
- **Assembly** (BUILD_GUIDE step 7). Set the nyloc to about 0.3 mm of end play **while holding the bolt head with the 2.5 mm key from inside the tub**. Otherwise the nyloc turns the bolt and undoes its 0.04 N·m snug, and the wall nut is then behind the hub.
- **Slicing.** The round-4 slice (1.16 h, 2 per plate) is stale: re-slice after the reviews.

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Running bore | Ø3.5 printed (Ø3.7 CAD), 14.8 long | +0.15/−0 | running fit on M3, 0.5 clearance | HOLE_COMP +0.2 | default from fdm-design-rules (no library row) |
| Pitch radius | 16.18 | ±0.15 | matches the 10 mm link pitch | — | rover_frame.RP |
| Hub inner end (round 5) | world \|y\| 43.7 (z −11.3 in the sprocket frame); part 14.8 tall | ±0.2 | seats on the running washer on the wall nut | — | rover_frame.IDLER_HUB_Y0 |

Printed targets for the whole rover: see the chassis brief. `print_requirements.json` now asks for `elefant_foot_compensation` 0.2, so the bore's first layer doesn't narrow (DFM round 2, R1).

## Parameters exposed by model.py
ROUND_BORE (+ the sprocket model's parameters, including HUB_Z0_ROUND from rover_frame.IDLER_HUB_Y0). `cad_checks.py` proves them on the geometry (5 checks: size 14.8 tall, bore through, hub from |y| 43.7, disc and teeth, no sprocket slots).

## Risks
- **Bore wear on the bolt threads:** class 12.9 bolts, and a 0.5 mm running clearance.
- **Idler creeping back under the track pull:** the jack screw holds it. Proof test 1 confirms it with the disc measurement; the pen mark is now on the head washer and head plate inside the tub, because the wall nut is behind the hub.
- **Shorter bore (round 5):** about 1.9° of cock on the bolt instead of 1.4°, which the links take out (see above). Keep the end play at about 0.3 mm, under the spec's 0.5.
