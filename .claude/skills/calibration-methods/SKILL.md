---
name: calibration-methods
description: How each MK3 calibration test works and how to turn the user's measurements into numbers. Covers the temperature tower, single-wall flow cube, Linear Advance K, dimensional cube and hole/fit gauge, and the optional layer-adhesion coupon, plus formulas, plausible ranges and the measurement protocol. Use when planning, generating, analyzing or building calibration tests.
---

# Calibration methods (MK3, stock firmware)

Calibrate per material **and** per spool brand. Re-check when changing spool brand, nozzle or sheet. Results go to `library/materials.csv` through the librarian, and the newest row wins.

## Measurement protocol (put this in every calibration `inspection.md`)

- Calipers zeroed. Take three readings per dimension at mid-height, away from the seam. Record every reading, not just the mean.
- Measure only once the part is at room temperature, at least 15 minutes after removal.
- Note the spool brand and colour, the sheet, and anything odd: warping, stringing, under-extrusion.

## 1. Temperature tower → `nozzle_c`

- A tower of segments, each printed 5 °C apart (the post-processor inserts `M104 S<t>` at each segment's Z). Test from the top of the filament's range down to the bottom.
- The user rates each segment for surface, bridging and stringing, then bends a thin fin at each level by hand to compare layer bonding.
- **Result:** for structural parts, the highest temperature without bad stringing or sag. Layer bonding improves with heat.
- **Plausible:** inside the tested range. If the best is at an edge, extend the range and repeat.

## 2. Flow: single-wall cube → `flow_ratio`

- A 30 mm cube printed in vase mode or with one perimeter, no top, extrusion width w (0.45).
- Measure the wall at 4 sides × 3 readings = t_m (mean).
- **Result:** `flow_ratio = current_extrusion_multiplier × w / t_m`
- **Plausible:** 0.90–1.10. Outside that, suspect a measurement error, a wet filament or a partial clog.

## 3. Linear Advance → `la_k`

- The MK3 firmware runs Linear Advance 1.5: `M900 K`, typically 0.0–0.2.
- Prusa's filament profiles send two values, a LA 1.5 value (for example PETG 0.08) plus a legacy value above 10 that the firmware ignores. Don't treat the legacy value as an error.
- **Pattern:** lines that alternate slow and fast segments, with K stepping from start to end, e.g. 0 → 0.1 in 0.01 steps. Each line is labelled by its K.
- The user picks the line with the most uniform width across the speed changes: no bulge at the slow→fast transition, no gap at fast→slow.
- **Result:** that K. It is applied by the user in the PrusaSlicer filament profile's start G-code (`M900 K<value>`); agents never edit custom G-code.
- **Plausible:** not at the first or last line of the pattern.

## 4. Dimensions and fits → `xy_comp_mm`, `hole_comp_mm`, `xy_shrink_pct`

The test prints a 20 × 20 × 20 mm cube, a gauge with vertical holes of Ø 3/5/8/10 mm modelled at nominal (no compensation), and matching pegs.

- **Outer XY.** Mean measured X and Y = m.
  - `xy_shrink_pct = 100 × (20 − m) / 20`
  - If |shrink| < 0.5 %, use `xy_comp_mm = (20 − m) / 2` (PrusaSlicer's `xy_size_compensation` acts per side).
  - Otherwise report shrinkage (scale the model) instead of an offset. ASA, PC and PA often shrink.
- **Holes.** For each nominal Ø_n with measured mean Ø_m, the error is e = Ø_n − Ø_m.
  - `hole_comp_mm = mean(e)`, added to the modelled diameter through `HOLE_COMP`.
  - If max(e) − min(e) > 0.1 mm, record a per-size table in the notes. Small holes usually shrink more.
- **Fits.** For each peg/hole pair, record press / snug / sliding / loose. Report the smallest diametral clearance that slides; that becomes the "sliding fit" value for this material.
- **Plausible:** hole_comp 0.05–0.5 mm, |xy_comp| ≤ 0.15 mm.

## 5. Layer adhesion (optional) → `z_strength_ratio`

- Print two identical bars, for example 80 × 10 × 4 mm. Print one flat (layers along the bar's length) and one standing upright (layers across it).
- Load both to failure as cantilevers with the same lever arm, using a luggage scale or hanging weights.
- **Result:** `z_strength_ratio = F_upright / F_flat`
- **Plausible:** 0.2–0.9. Below 0.3, suspect a temperature that's too low or too much fan.

## `calibration_result.json` shape (produced by `tools/calibration/analyze.py`)

```json
{"job_id": "...", "test": "dims", "material": "PETG", "brand": "Prusament", "color": "Galaxy Black",
 "inputs": {"...": "every reading used"},
 "results": {"xy_comp_mm": 0.04, "hole_comp_mm": 0.22, "xy_shrink_pct": 0.3},
 "plausible": true, "notes": "...", "lead_review": null}
```
