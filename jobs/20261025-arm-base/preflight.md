# Preflight: Robot arm base (×1: 1 copy × 1 plate)

Job: 20261025-arm-base · print-ops-lead · 2026-10-26 · confirm each item at approval and again at the printer.

- [ ] **Plates:** 1 plate, 1 base on it.
- [ ] **Filament:** PETG, loaded (`config/printer.json` lists no materials on hand yet, so confirm you have it). The G-code uses the Prusament PETG profile: 240 °C on the first layer, then 250 °C; bed 85 °C, then 90 °C. Have at least **132 g** on the spool (119.5 g + 10 %). The base prints almost solid.
- [ ] **Drying:** if the spool has been out of its bag for more than a few days, dry it first (65 °C, 4 h). Wet PETG strings and prints weak.
- [ ] **Sheet:** smooth PEI, cleaned with isopropyl alcohol, then a thin, even **glue-stick** layer as a release layer. PETG bonds hard to bare smooth PEI, and the base's 4 mm solid top plate is all on the bed. Let the sheet cool fully before you take the base off.
- [ ] **Bed clear** of objects and old prints; nozzle clean.
- [ ] **First layer:** the base prints upside down, top plate on the bed: a 110 × 104 mm plate with the servo window, lead notches and pilots in it.
- [ ] **SD card file:** `1025_arm_base.gcode` (written by `tools/export_sd.py` after you approve).
- [ ] **On the printer:** Print from SD → `1025_arm_base.gcode`. Watch the whole first layer (about 23 min).
- [ ] **Time:** about **8.7 h**. Decide whether someone will be nearby: the printer is offline, so nothing reports a failure.
- [ ] **Screw-strip check:** spec §8 doesn't ask for one on the base. Its notch-to-pilot strips are 2.0 mm printed, above the 1.8 mm rule. The user's first-print check belongs to the forearm and the claw frame.

**After printing:**
- If the MG996R is tight going into its window, scrape the two seam lines on the window's end face nearest the near-tab pilots (audit note 2).
- Spec §8 at assembly: the servo goes in from above, case bottom first, with its lead through an end notch, and its tab screws bite in all 4 pilots.
- Strength is NEEDS_TEST: run spec §8's proof test (arm-up push, 77 N on the rim, USB plug ×5) and record it in inspection.md.
