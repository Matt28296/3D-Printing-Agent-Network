VERDICT: FAIL

# DFM review (round 5, independent): 20261026-arm-claw-frame

Reviewer: dfm-reviewer (independent; did not design the part) · 2026-10-26 · round 5 (V-groove for the cover's post),
merged at 022af2e. The CAD engineer's round-5 recheck (designer's own) is replaced by this review.

## Inputs

- **This job:** model.py, design_brief.md, cad_checks.py, geometry.json, mesh_check.json, and git history of this file
  and strength.md.
- **Shared:** claw_frame.py (`VSEAT_*`, `ANCHOR_*`, `Z_TOP0`). The cover's model and review. BUILD_GUIDE §4 step 9.
- **Skills:** fdm-design-rules, prusaslicer-settings, build123d-cad, strength-checks.

**Re-run here:**
- `cad_checks.py` (21/21, exit 0).
- **Exact-solid sections** of the groove at y 26 and y 30, its fit with the cover's ridge, and the ligament to the
  anchor pilot.
- **A scratch slice of this job's committed part.stl** with the arm's command (slice_settings.json: PrusaSlicer 2.7.2,
  0.20mm QUALITY @MK3, Prusament PETG, slice_overrides.ini). The G-code was read back at the groove, the pilot and the
  top layers.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit, one watertight solid, min Z 0 | PASS | 42.85 × 64.0 × 48.5, 1 solid, `fits_bed` (geometry.json) |
| 2 | Orientation, load paths vs layers | PASS | Back face on the bed, unchanged. The groove's +x flank takes the cover's push: bearing on the layer corners, and interlayer shear along the groove's bottom for the block in front. Both are in strength.md (3.61, 6.66) |
| 3 | The groove prints open upward | PASS | Both flanks face up at 45°: no overhang, no bridge. In the G-code the groove is a stack of slots, 0.3 / 0.7 / 1.1 / 1.5 wide, in the layers ending 17.2 / 17.4 / 17.6 / 17.8, each bounded by external perimeters centred on x 15.25 |
| 4 | The groove's 0.3 mm first-layer slot | PASS (note) | Sliced as a 0.3 slot between two external perimeters, so it will close up. Harmless only while the cover's ridge tip stays above 17.2. Today the tip clears it by 0.006 at the nominal seat; the cover's fix puts the tip at 17.35 |
| 5 | Walls ≥ 0.9; the ligament to the anchor pilot | PASS (note) | 0.95 CAD at the block top (x 16.05 → 17.0), +1 mm per mm down. In the G-code the top layer prints it as two external perimeters, 0.52 wide each, solid. It does take the M3's thread-forming pressure: strength info row 63 (2.55 Lame on the thinnest layer, ≈3.0 averaged; installation only, backed by the screw). Add the first-assembly check suggested in the report |
| 6 | **Mating datum on a slice plane** | **FAIL** | The bulkhead top, z 48.5, is the cover's z datum (its top wall sits there) and the reference for rack A's guide. It lies exactly on the slice plane of layer 48.4–48.6. In the arm's slice it prints at **48.4**: the last layer is `;Z:48.4` and the slicer dropped the layer whose slice plane is the face. That is decided by floating-point rounding at the plane, not by design. The cover's V-seat fix needs it fixed: a 0.1 mm swing to 48.6 would put 0.04–0.2 mm of play back at the ridge (cover strength.md) |
| 7 | Rail block top | PASS (recorded) | CAD 17.75 prints at **17.8**: layer 17.6–17.8 is sliced at 17.7, 0.05 from the face, so this is deterministic. The cover's foot flats, 0.1 over the block in CAD, are therefore 0.05 over it in print. That is the cover's finding; the cover's fix raises its flats to 0.30 |
| 8 | Groove x span; alignment with the cover's ridge | PASS | Sections at y 26 and 30: groove x 14.45–16.05 at z 17.75, apex (15.25, 16.95), the same constant (`VSEAT_XC` 15.25) as the ridge. Fit 0 mm³, 0.0707 normal gap per flank (CAD). Round 4's text 14.35–15.95 differed from round 4's own what-if (`LIP_X0 + 0.1` = 14.45), which is what was built; it costs 0.1 of ligament (item 5) |
| 9 | HOLE_COMP; holes | PASS | Unchanged: clamp Ø2.6, 3 × Ø2.7 pilots (anchor pilot at (18.35, 28), z 3.75–17.75), 2 × Ø2.2 flat-topped front pilots |
| 10 | Bottom chamfer | PASS | 0.4 mm, unchanged |
| 11 | Fasteners per §4 | PASS on this part | The M3 × 45 self-taps into a Ø2.5 printed pilot, 10.75 engaged with the washer. Assembled a few times. Pull-out 4.22 on the preload (sustained) |
| 12 | Named parameters | PASS | `VSEAT_D`, `VSEAT_XC`, `VSEAT_Y0` (claw_frame.py), `GROOVE_Y` (model.py) |
| 13 | cad_checks | PASS | 21/21, exit 0 |

## Required fix

**One frame change, part of the cover's V-seat fix:**
- **Change:** the bulkhead's top to **z 48.45** in the frame's model.py (a frame-only constant).
- **Unchanged:** the cover's `Z_TOP0` stays 48.5; the bulkhead's M3 pilots keep their depth below the new top.
- **Printed result:** it prints at 48.4, the same height as today, but now with 0.05 mm to the slice planes on both
  sides (48.3 and 48.5), so no slicer rounding can move it.
- **CAD:** the cover's top wall then has a 0.05 CAD gap over the bulkhead. Change `claw_sequence_check.py`'s declared
  contact plane (`z = Z_TOP0`, "top wall on the bulkhead top") to match.

Everything else on this part passes. The cover's review lists the rest of the fix: `VSEAT_CLR` 0, its flats at 18.05,
its tip at 17.35, and the BUILD_GUIDE step-9 order and check. None of it changes this part's geometry.

## Notes

1. **Re-slice** after the fix: the committed G-code (Oct 26 01:24) predates the round-3 to round-5 geometry.
2. **The tab-pilot strips** (user-accepted 26 Oct 2026) are unchanged; spec §8 has the screw-strip check.

---

## History

- **Round 4** (independent; git a701995): PASS. The anchor pilot was added.
- **Round 5 self-check** (cad-engineer): PASS. Superseded by this review.
